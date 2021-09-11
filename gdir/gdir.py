import argparse
import locale
import os
import sys

from googlemaps import exceptions as ge

from gdir.cctld import CCTLDS
from gdir.directions import Directions
from gdir.directions import NotFoundError


def parse_time(time_str):
    try:
        minute = hour = day = month = year = None
        days_delta = 0
        s = time_str

        if '+' in s:
            assert(s.count('+') == 1)
            s, days_delta = s.split('+')
            days_delta = int(days_delta)

        s, minute = s[:-2], s[-2:]
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

        return {'time_str': time_str, 'days_delta': days_delta, 'minute': minute, 'hour': hour,
                'day': day, 'month': month, 'year': year}
    except:
        raise argparse.ArgumentTypeError('{}: Invalid time specification'.format(time_str))

def parse_cctld(s, cctlds=CCTLDS):
    if s not in cctlds:
        raise argparse.ArgumentTypeError('{}: Invalid ccTLD code'.format(s))
    return s

def main():
    description = """
    Query the Google Directions API and write results to the standard output in human-readable format. Uses public transport (\'transit\') mode by default. Requires environment variable GOOGLE_MAPS_API_KEY defining a valid API key. Language of directions is determined from locale configuration using locale.getdefaultlocale(), which reads from LC_ALL, LC_CTYPE, LANG and LANGUAGE in descending order of priority. Word wrapping is achieved using shutil.get_terminal_size(), which reads from COLUMNS and which may alternatively use system calls to determine the terminal width, using a fall-back value of 80 if the terminal width could not be determined. Scripts may use the -N flag (see below) to disable word wrapping but should not make excessive assumptions about the structure of output: When using the -N flag, valid assumptions are 1) routes are delimited by empty lines 2) each route may be represented as a two-column table, where rows are separated by newlines and where the first and second column in the table are separated by a single space 3) values in the first column may be left-padded with a variable amount of whitespace 4) the format of values in the first column may vary for all rows, including the first row 5) route output may be followed by two empty lines, followed by travel warnings and/or copyright/transport agency information. Status codes: 0 success; 1 generic error; 2 invalid argument; 3 origin/desination not found; >=4 google-maps-services-python exceptions.
    """
    epilog = """
Departure and arrival times are expressed in terms of local time at the origin and destination, respectively. Times must be specified in the form [[[[cc]yy]mm]dd]HH[:]MM[+N], where ccyy is the year, mm is the month (ranging from 1 to 12), dd is the day (ranging from 1 to 31), HH is the hour (ranging from 0 to 23) and MM is the minute (ranging from 0 to 59). When left unspecified, ccyy, mm and dd values are assumed to be the current year, month and day, respectively. For ambiguous times arising from daylight saving transitions, it is assumed that the ambiguous time is expressed in the time zone's standard time. The suffix +N may be used to offset the specified time by N days. Thus, 12:00+1 means 'tomorrow at noon'.
    """

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('origin', help='start address (quote-enclosed) or latitude,longitude pair')
    parser.add_argument('destination', help='end address (quote-enclosed) or latitude,longitude pair')

    parser.add_argument('-b', '--bus', action='store_const', const='bus', help='prefer to travel by bus')
    parser.add_argument('-r', '--rail', action='store_const', const='rail', help='prefer to travel by rail (equivalent to train, tram, underground)')
    parser.add_argument('-n', '--train', action='store_const', const='train', help='prefer to travel by train')
    parser.add_argument('-m', '--tram', action='store_const', const='tram', help='prefer to travel by tram')
    parser.add_argument('-u', '--underground', action='store_const', const='subway', help='prefer to travel by underground (a.k.a. subway)')

    parser.set_defaults(mode='transit')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--car', dest='mode', action='store_const', const='driving', help='travel by car instead of public transport')
    group.add_argument('-k', '--bicycle', dest='mode', action='store_const', const='bicycling', help='travel by bicycle instead of public transport')
    group.add_argument('-f', '--foot', dest='mode', action='store_const', const='walking', help='travel on foot instead of public transport')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--depart', dest='departure_time', metavar='time_arg', type=parse_time, help='set departure time (see below)')
    group.add_argument('-a', '--arrive', dest='arrival_time', metavar='time_arg', type=parse_time, help='set arrival time (see below)')

    parser.add_argument('-S', '--substeps', dest='include_substeps', action='store_true', help='show sub-steps in output')
    parser.add_argument('-M', '--multiple', dest='alternatives', action='store_true', help='show multiple routes, if available')
    parser.add_argument('-N', '--no-wrap', dest='text_wrap', action='store_false', help='disable word wrapping (affects command line mode only; potentially useful for scripting)')

    parser.add_argument('-R', '--region', metavar='region_code', type=parse_cctld, help='set region bias using the specified top-level domain two-character code (ccTLD)')
    parser.add_argument('-C', '--copyright', action='store_true', help='display copyright and transport agency information (see Directions API terms and conditions)')

    args = parser.parse_args()
    transit_modes = [m for m in (args.rail, args.train, args.tram, args.bus,
                                 args.underground) if m is not None]

    if 'GOOGLE_MAPS_API_KEY' not in os.environ:
        print('Environment variable GOOGLE_MAPS_API_KEY undefined', file=sys.stderr)
        sys.exit(2)

    try:
        directions = Directions(args.origin, args.destination, args.mode,
                                transit_modes,
                                args.departure_time,
                                args.arrival_time, args.region, args.alternatives,
                                os.environ['GOOGLE_MAPS_API_KEY'], locale.getdefaultlocale()[0],
                                args.copyright)
        print(directions.to_str(args.include_substeps, args.text_wrap), end='')

    except ValueError as e:
        print(e, file=sys.stderr)
        sys.exit(2)

    except NotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(3)

    except ge.ApiError as e:
        print(e, file=sys.stderr)
        sys.exit(4)

    except ge.TransportError as e:
        print(e, file=sys.stderr)
        sys.exit(5)

    except ge.HTTPError as e:
        print(e, file=sys.stderr)
        sys.exit(6)

    except ge.Timeout as e:
        print(e, file=sys.stderr)
        sys.exit(7)
