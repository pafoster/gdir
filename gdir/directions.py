import datetime
import re
import shutil
import textwrap

import colorama
from colorama import Style
import googlemaps
from googlemaps.exceptions import ApiError
import pytz

colorama.init()


class NotFoundError(Exception):
    pass

class Directions:
    def __init__(self, origin, destination, mode, transit_modes, departure_time, arrival_time, region,
                 alternatives, maps_key, language, display_copyrights):
        if departure_time or arrival_time:
            # Request directions while omitting departure or arrival times to obtain latitude and
            # longitude of origin and destination
            directions = Directions._get_directions(origin, destination, mode, transit_modes,
                                                    None, None,
                                                    region, alternatives, maps_key, language)

            if departure_time:
                origin_timezone = directions[0]['legs'][0]['departure_time']['time_zone']
                departure_time = Directions._convert_local_time(origin_timezone,
                                                                departure_time)
            if arrival_time:
                dest_timezone = directions[0]['legs'][0]['arrival_time']['time_zone']
                arrival_time = Directions._convert_local_time(dest_timezone,
                                                              arrival_time)

        directions = Directions._get_directions(origin, destination, mode, transit_modes,
                                                departure_time,
                                                arrival_time, region, alternatives,
                                                maps_key, language)

        self.routes = [Route(d) for d in directions]

        self.copyrights = set()
        self.warnings = set()
        self.agencies = set()
        for d in directions:
            if d['copyrights']:
                self.copyrights.add(d['copyrights'])
            if d['warnings']:
                self.warnings = self.warnings.union(set(d['warnings']))
            for step in d['legs'][0]['steps']:
                if 'transit_details' in step and 'agencies' in step['transit_details']['line']:
                    for agency in step['transit_details']['line']['agencies']:
                        self.agencies.add((agency['name'], agency['url']))

        self.display_copyrights = display_copyrights

    @staticmethod
    def _convert_local_time(timezone, time):
        time_str = time.pop('time_str')
        days_delta = time.pop('days_delta')

        try:
            timezone = pytz.timezone(timezone)
            # Get current local time at the specified time zone
            current_time = datetime.datetime.now(timezone)
            # Use current local time to infer any missing year, month, day information
            for k in 'year', 'month', 'day':
                if time[k] is None:
                    time[k] = getattr(current_time, k)

            return timezone.localize(datetime.datetime(**time) +
                                     datetime.timedelta(days=days_delta), is_dst=False)
        except ValueError as ex:
            raise ValueError('{}: invalid time specification, {}'.format(time_str, str(ex)))

    @staticmethod
    def _get_directions(origin, destination, mode, transit_modes, departure_time, arrival_time, region,
                       alternatives, maps_key, language):

        gmaps = googlemaps.Client(key=maps_key)

        try:
            directions = gmaps.directions(origin=origin, destination=destination, mode=mode,
                                          transit_mode=transit_modes,
                                          alternatives=alternatives,
                                          region=region,
                                          departure_time=departure_time,
                                          arrival_time=arrival_time,
                                          language=language)

        except ApiError as ex:
            if str(ex) == 'NOT_FOUND':
                raise NotFoundError('{} -> {}: No directions found'.format(origin, destination))
            else:
                raise ex

        if len(directions) == 0:
            raise NotFoundError('{} -> {}: No directions found'.format(origin, destination))

        return directions

    def to_str(self, include_substeps, text_wrap):
        s = '\n'.join([r.to_str(include_substeps, text_wrap) for r in self.routes])

        if (len(self.copyrights) > 0 or len(self.agencies) > 0) and self.display_copyrights or len(self.warnings) > 0:
            s += '\n'
        if len(self.warnings) > 0:
            s += '\n' + '\n'.join(self.warnings)
        if len(self.copyrights) > 0 and self.display_copyrights:
            s += '\n' + ' '.join(self.copyrights)
        if len(self.agencies) > 0 and self.display_copyrights:
            s += '\n' + '\n'.join([' '.join(agency) for agency in self.agencies])
        if (len(self.copyrights) > 0 or len(self.agencies) > 0) and self.display_copyrights or len(self.warnings) > 0:
            s += '\n'

        return s

class Route:
    def __init__(self, directions):
        leg = directions['legs'][0]

        self.start_address = leg['start_address']
        self.end_address = leg['end_address']
        self.distance = leg['distance']['text'].replace(' ', '')

        if 'departure_time' in leg.keys() and 'arrival_time' in leg.keys():
            self.departure_time = leg['departure_time']['text']
            self.arrival_time = leg['arrival_time']['text']
            self.modalities = \
                [s['transit_details']['line']['vehicle']['name'] for s in leg['steps']
                 if s['travel_mode'] == 'TRANSIT' and
                 'vehicle' in s['transit_details']['line']]
        else:
            self.duration = leg['duration']['text'].replace(' ', '')

        self.steps = [Step(s) for s in leg['steps']]

    @staticmethod
    def _get_terminal_ncolumns():
        return shutil.get_terminal_size(fallback=(80, 24))[0]

    def _generate_step_table(self, include_substeps):
        for n, step in enumerate(self.steps):
            # TODO We could make a TransitStep class instead, and omit the travel_mode inst. var
            if step.travel_mode != 'TRANSIT':
                yield step.duration + ' ', '{} {}'.format(step.instructions, step.distance)

                if len(step.substeps) > 0 and include_substeps:
                    for m, substep in enumerate(step.substeps):
                        yield str(m+1) + ' ', '{} {}'.format(substep[0], substep[1])
            else:
                yield ('{}-{} '.format(step.departure_time,
                                       step.arrival_time),
                       '{} board {} {} towards {} alight at {}'.format(
                           step.departure_stop.upper(),
                           step.short_name.title(),
                           step.vehicle_name.lower(),
                           step.headsign, step.arrival_stop.upper()))

    def _wrap_text(text, width, prefix_first_line='', prefix_subsequent_lines=''):
        # NB Text wrap fails if we include non-printable characters, i.e. colorama
        return '\n'.join([prefix_subsequent_lines + l if n > 0 else prefix_first_line + l
                          for n, l in enumerate(textwrap.wrap(text,
                                                              width=width))])

    def to_str(self, include_substeps, text_wrap):
        n_columns = Route._get_terminal_ncolumns()
        col1_width = max([len(col1) for col1, _ in
                          Route._generate_step_table(self, include_substeps)])

        s = ''
        if hasattr(self, 'departure_time') and hasattr(self, 'arrival_time'):
            col1_width = max([col1_width, len('{}-{} '.format(self.departure_time, self.arrival_time))])
            s += '{}-{} ({}) {} -> {} {}'.format(Style.BRIGHT+self.departure_time+Style.RESET_ALL,
                                                 Style.BRIGHT+self.arrival_time+Style.RESET_ALL,
                                                 ''.join([m.upper()[0] for m in self.modalities]),
                                                 self.start_address,
                                                 self.end_address,
                                                 self.distance)
        else:
            col1_width = max([col1_width, len('{} '.format(self.duration))])
            s += '{} {} -> {} {}'.format(Style.BRIGHT+self.duration+Style.RESET_ALL,
                                         self.start_address,
                                         self.end_address,
                                         self.distance)
        if n_columns > 0 and text_wrap:
            # We search for offset because string contains non-printable characters
            offset = s.find(' ') + 1
            s = Route._wrap_text(s[offset:], n_columns-col1_width, s[:offset],
                                 ' '*col1_width)
        s += '\n'

        for col1, col2 in Route._generate_step_table(self, include_substeps):
            col1 = ' ' * (col1_width - len(col1)) + col1
            if n_columns > 0 and text_wrap:
                col2 = Route._wrap_text(col2, n_columns-col1_width,
                                        prefix_subsequent_lines=' '*col1_width)
            s += '{}{}\n'.format(col1, col2)

        return s

class Step:
    def __init__(self, step):
        self.substeps = []

        self.travel_mode = step['travel_mode']
        if self.travel_mode != 'TRANSIT':
            self.instructions = Step._strip_html(step['html_instructions'])
            self.distance = step['distance']['text'].replace(' ', '')
            self.duration = step['duration']['text'].replace(' ', '')

            if 'steps' in step.keys():
                self.substeps = [(Step._strip_html(s['html_instructions']),
                                 s['distance']['text'].replace(' ', ''))
                                 for s in step['steps'] if 'html_instructions' in s]

        else:
            self.departure_time = step['transit_details']['departure_time']['text']
            self.arrival_time = step['transit_details']['arrival_time']['text']
            self.departure_stop = step['transit_details']['departure_stop']['name']
            self.arrival_stop = step['transit_details']['arrival_stop']['name']

            self.short_name = ''
            self.vehicle_name = ''
            self.headsign = '<unknown>'
            if 'short_name' in step['transit_details']['line'].keys():
                self.short_name = step['transit_details']['line']['short_name']
            if 'vehicle' in step['transit_details']['line'].keys():
                self.vehicle_name = step['transit_details']['line']['vehicle']['name']
            if 'headsign' in step['transit_details'].keys():
                self.headsign = step['transit_details']['headsign']
            if self.short_name == '' and self.vehicle_name == '':
                self.vehicle_name = '<unknown>'

    @staticmethod
    def _strip_html(s):
        # TODO Regex to replace all entities
        return re.sub('<[^<]+?>', '', s).replace('&nbsp;', '')
