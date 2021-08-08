gdir: Get Train/Bus Times Using the Command Line
=========================

``gdir`` is a command line tool which queries Google Directions for public transport routes. The tool displays results as human-readable text.

Installation
-------------------------
``gdir`` is listed on the `Python Package Index <https://pypi.org>`_ and may be installed using ``pip`` as follows:

.. code:: shell-session

    $ pip install gdir

Configuration
-------------------------
You will need a Google Directions API key. See `Google Directions API documentation <https://developers.google.com/maps/documentation/directions/get-api-key>`_ for instructions on how to obtain a key.

Set the shell environment variable GOOGLE_MAPS_API_KEY to your API key. This typically involves adding something like the following to your ``.profile`` file:

.. code:: bash

    export GOOGLE_MAPS_API_KEY="XXXXXXXXXXXXXXXX-XXXXXXXXXXXXX-XXXXXXXX"

Example Usage
-------------------------
Display directions for travelling from Tower Bridge, London to Buckingham Palace, using any mode of public transport:

.. code:: shell-session

    $ gdir "Tower Bridge, London" "Buckingham Place"

    09:15-09:43*U Tower Bridge, Tower Bridge Rd, London SE1 2UP, UK -> London SW1A 1AA, UK 6.0km
         12mins Walk to London Bridge 0.9km
    09:27-09:33 LONDON BRIDGE board Jubilee underground towards Stanmore alight at GREEN PARK
         10mins Walk to London SW1A 1AA, UK 0.8km

Display directions for the same origin and destination, but prefer to travel by bus and depart at 10:00am:

.. code:: shell-session

    $ gdir -b -d 10:00 "Tower Bridge, London" "Buckingham Place"

    10:10-10:43*BB Tower Bridge, Tower Bridge Rd, London SE1 2UP, UK -> London SW1A 1AA, UK 6.8km
          4mins Walk to Boss Street (Stop T) 0.3km
    10:13-10:27 BOSS STREET (STOP T) board 381 bus towards Waterloo alight at WATERLOO STATION /
                YORK ROAD (STOP W)
          3mins Walk to Westminster Cathedral / Victoria Station (Stop M) 0.2km
    10:34-10:35 WESTMINSTER CATHEDRAL / VICTORIA STATION (STOP M) board 11 bus towards Walham Green
                alight at VICTORIA STATION (STOP G)
         10mins Walk to London SW1A 1AA, UK 0.8km

Display multiple options for travelling from London to Edinburgh, arriving by 2pm on 10th August:

.. code:: shell-session

    $ gdir -a 081014:00 -M "London" "Edinburgh" 
    
    09:00-13:20*T London, UK -> Edinburgh, UK 632km
    09:00-13:20 KING'S CROSS board Lner train towards Edinburgh alight at EDINBURGH WAVERLEY
    
    08:30-13:12*T London, UK -> Edinburgh, UK 632km
    08:30-13:12 KING'S CROSS board Lner train towards Edinburgh alight at EDINBURGH WAVERLEY
    
    08:10-13:29*TT London, UK -> Edinburgh, UK 644km
    08:10-11:50 LONDON EUSTON board Avanti west coast train towards Glasgow Central alight at
                CARLISLE
    12:07-13:29 CARLISLE board Transpennine express train towards Edinburgh alight at EDINBURGH
                WAVERLEY
    
    08:00-12:20*T London, UK -> Edinburgh, UK 632km
    08:00-12:20 KING'S CROSS board Lner train towards Edinburgh alight at EDINBURGH WAVERLEY

**Note**: If you get a *no directions found* error, try appending the city to your origin/destination address.  See also the ``-R`` flag below for setting region bias.

Detailed Help and List of Command Line Arguments
-------------------------
.. code:: none

    usage: gdir [-h] [-r] [-n] [-m] [-b] [-u] [-d time_arg | -a time_arg] [-S] [-M] [-N]
                [-R region_code]
                origin destination
    
    Query the Google Directions API using public transport ('transit') mode and write results to
    the standard output in human-readable format. Requires environment variable
    GOOGLE_MAPS_API_KEY defining a valid API key. Language of directions is determined from locale
    configuration using locale.getdefaultlocale(), which reads from LC_ALL, LC_CTYPE, LANG and
    LANGUAGE in descending order of priority. Word wrapping is achieved using
    shutil.get_terminal_size(), which reads from COLUMNS and which may alternatively use system
    calls to determine the terminal width, using a fall-back value of 80 if the terminal width
    could not be determined.
    
    positional arguments:
      origin                start address (quote-enclosed) or latitude,longitude pair
      destination           end address (quote-enclosed) or latitude,longitude pair
    
    optional arguments:
      -h, --help            show this help message and exit
      -r, --rail            prefer to travel by rail (equivalent to train, tram, underground)
      -n, --train           prefer to travel by train
      -m, --tram            prefer to travel by tram
      -b, --bus             prefer to travel by bus
      -u, --underground     prefer to travel by underground (a.k.a. subway)
      -d time_arg, --depart time_arg
                            set departure time (see below)
      -a time_arg, --arrive time_arg
                            set arrival time (see below)
      -S, --substeps        show sub-steps in output
      -M, --multiple        show multiple routes, if available
      -N, --no-wrap         disable word wrapping (affects command line mode only; potentially
                            useful for scripting)
      -R region_code, --region region_code
                            set region bias using the specified top-level domain two-character
                            code (ccTLD)
    
    Departure and arrival times are expressed in terms of local time at the origin and
    destination, respectively. Times must be specified in the form [[[[cc]yy]mm]dd]HH[:]MM, where
    ccyy is the year, mm is the month (ranging from 1 to 12), dd is the day (ranging from 1 to
    31), HH is the hour (ranging from 0 to 23) and MM is the minute (ranging from 0 to 59). When
    left unspecified, ccyy, mm and dd values are assumed to be the current year, month and day,
    respectively. For ambiguous times arising from daylight saving transitions, it is assumed that
    the ambiguous time is expressed in the time zone's standard time.

