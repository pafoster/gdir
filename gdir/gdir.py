import argparse
import locale
import os
import sys

from gdir.cctld import CCTLDS
from gdir.directions import Directions
from googlemaps.exceptions import ApiError

# TODO Implement terminal interface using ncurses dialog 
#   Origin and destination become optional, and we introduce a flag -T:
#   If any of the positional arguments (origin and destination) are omitted or if -T flag is selected, enter terminal mode.
#   This way, we can allow the user to enable terminal mode and supply flags!
#   Any specified command line arguments have the effect of setting the default value for the relevant dialogue screens:
#   1) InputMenu widget (Origin, Destination, mode, date, etc.) 
#   2) Use relevant dialogues for editing (date/time pickers etc.) 
#   3) (OPTIONAL-DO THIS LATER) Display results using a menu: The top level allows the use to select the route alternative, a sub-menu displays route steps, a sub-sub menu displays sub-steps (if any, otherwise display a message saying that no sub-step information is available).

def parse_time(time_str):
    try:
        minute = hour = day = month = year = None

        s, minute = time_str[:-2], time_str[-2:]
        assert(len(minute) == 2)
        minute = int(minute)

        if s[-1] == ':':
            s = s[:-1]

        s, hour = s[:-2], s[-2:]
        assert(len(hour) == 2)
        hour = int(hour)

        if len(s) > 0:
            s, day = s[:-2], s[-2:]
            assert(len(day) == 2)
            day = int(day)
        if len(s) > 0:
            s, month = s[:-2], s[-2:]
            assert(len(month) == 2)
            month = int(month)
        if len(s) > 0:
            if len(s) > 2:
                s, year = s[:-4], s[-4:]
            else:
                s, year = s[:-2], '20' + s[-2:]

            assert(len(year) == 4)
            year = int(year)

        return {'time_str': time_str, 'minute': minute, 'hour': hour, 'day': day,
                'month': month, 'year': year}
    except:
        raise argparse.ArgumentTypeError('{}: Invalid time specification'.format(time_str))

def parse_cctld(s, cctlds=CCTLDS):
    if s not in cctlds:
        raise argparse.ArgumentTypeError('{}: Invalid ccTLD code'.format(s))
    return s

def main():
    description = """
    Query the Google Directions API using public transport (\'transit\') mode and write results to the standard output in human-readable format. Requires environment variable GOOGLE_MAPS_API_KEY defining a valid API key. Language of directions is determined from locale configuration using locale.getdefaultlocale(), which reads from LC_ALL, LC_CTYPE, LANG and LANGUAGE in descending order of priority. Word wrapping is achieved using shutil.get_terminal_size(), which reads from COLUMNS and which may alternatively use system calls to determine the terminal width, using a fall-back value of 80 if the terminal width could not be determined.
    """
    epilog = """
    Departure and arrival times are expressed in terms of local time at the origin and destination, respectively. Times must be specified in the form [[[[cc]yy]mm]dd]HH[:]MM, where ccyy is the year, mm is the month (ranging from 1 to 12), dd is the day (ranging from 1 to 31), HH is the hour (ranging from 0 to 23) and MM is the minute (ranging from 0 to 59). When left unspecified, ccyy, mm and dd values are assumed to be the current year, month and day, respectively. For ambiguous times arising from daylight saving transitions, it is assumed that the ambiguous time is expressed in the time zone's standard time.
    """

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('origin', help='start address (quote-enclosed) or latitude,longitude pair')
    parser.add_argument('destination', help='end address (quote-enclosed) or latitude,longitude pair')

    # parser.set_defaults(mode='transit')
    # group = parser.add_argument_group(description='Mode of transport').add_mutually_exclusive_group()
    # group.add_argument('-c', '--car', dest='mode', action='store_const', const='driving', help='travel by car instead of public transport')
    # group.add_argument('-b', '--bicycle', dest='mode', action='store_const', const='bicycling', help='travel by bicycle instead of public transport')
    # group.add_argument('-f', '--foot', dest='mode', action='store_const', const='walking', help='travel on foot instead of public transport')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--rail', dest='transit_mode', action='store_const', const='rail', help='prefer to travel by rail (equivalent to train, tram, underground)')
    group.add_argument('-n', '--train', dest='transit_mode', action='store_const', const='train', help='prefer to travel by train')
    group.add_argument('-m', '--tram', dest='transit_mode', action='store_const', const='tram', help='prefer to travel by tram')
    group.add_argument('-b', '--bus', dest='transit_mode', action='store_const', const='bus', help='prefer to travel by bus')
    group.add_argument('-u', '--underground', dest='transit_mode', action='store_const', const='subway', help='prefer to travel by underground (a.k.a. subway)')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--depart', dest='departure_time', metavar='time_arg', type=parse_time, help='set departure time (see below)')
    group.add_argument('-a', '--arrive', dest='arrival_time', metavar='time_arg', type=parse_time, help='set arrival time (see below)')

    parser.add_argument('-S', '--substeps', dest='include_substeps', action='store_true', help='show sub-steps in output')
    parser.add_argument('-M', '--multiple', dest='alternatives', action='store_true', help='show multiple routes, if available')
    parser.add_argument('-N', '--no-wrap', dest='text_wrap', action='store_false', help='disable word wrapping (affects command line mode only; potentially useful for scripting)')

    parser.add_argument('-R', '--region', metavar='region_code', type=parse_cctld, help='set region bias using the specified top-level domain two-character code (ccTLD)')
    parser.add_argument('-C', '--copyright', action='store_true', help='display copyright and transport company information (see Directions API terms and conditions)')

    args = parser.parse_args()

    if 'GOOGLE_MAPS_API_KEY' not in os.environ:
        print('Envionment variable GOOGLE_MAPS_API_KEY undefined', file=sys.stderr)
        sys.exit(1)

    try:
        directions = Directions(args.origin, args.destination, args.transit_mode,
                                args.departure_time,
                                args.arrival_time, args.region, args.alternatives,
                                os.environ['GOOGLE_MAPS_API_KEY'], locale.getdefaultlocale()[0],
                                args.copyright)
        print(directions.to_str(args.include_substeps, args.text_wrap), end='')

    except (ValueError, ApiError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
