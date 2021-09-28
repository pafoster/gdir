gdir: Get Train/Bus Directions Using the Command Line
-----------------------------------------------------

``gdir`` is a command line tool which queries Google Directions. The tool displays results as human-readable text.

|

.. figure:: https://github.com/pafoster/gdir/raw/main/img/gdir.gif
   :width: 576
   :alt: Gdir in Action

Installation
-------------------------
``gdir`` is listed on the `Python Package Index <https://pypi.org>`_ and may be installed using ``pip`` as follows:

.. code:: shell-session

    $ python -m pip install gdir

Configuration
-------------------------
You will need a Google Directions API key. See `Google Directions API documentation <https://developers.google.com/maps/documentation/directions/get-api-key>`_ for instructions on how to obtain a key.

Set the shell environment variable GOOGLE_MAPS_API_KEY to your API key. This typically involves adding something like the following to your ``.profile`` file:

.. code:: bash

    export GOOGLE_MAPS_API_KEY="XXXXXXXXXXXXXXXX-XXXXXXXXXXXXX-XXXXXXXX"

**Note**: If you don't want to set up your own API key, there is a `web-based version of gdir <https://gdir.telae.net>`_ - try viewing https://gdir.telae.net in a terminal-based browser like `links <http://links.twibright.com/>`_, `lynx <https://lynx.invisible-island.net/>`_, or `w3m <https://github.com/tats/w3m>`_! The web-based version implements most of the features described below.

Example Usage
-------------------------
Display directions from **Tower Bridge, London** to **Buckingham Palace**, using any mode of public transport and departing now:

.. code:: shell-session

    $ gdir "Tower Bridge, London" "Buckingham Place"

    08:02-08:30 (U) Tower Bridge, Tower Bridge Rd, London SE1 2UP, UK -> London SW1A
                1AA, UK 6.1km
          7mins Walk to Tower Hill 0.5km
    08:10-08:21 TOWER HILL board Circle underground towards Edgware Road alight at
                ST. JAMES'S PARK
         10mins Walk to London SW1A 1AA, UK 0.8km

Display directions for the same origin and destination, but prefer to travel by **bus** and **depart** at **10:00am today**:

.. code:: shell-session

    $ gdir -b -d 10:00 "Tower Bridge, London" "Buckingham Place"

    10:00-10:38 (BB) Tower Bridge, Tower Bridge Rd, London SE1 2UP, UK -> London
                SW1A 1AA, UK 7.0km
          4mins Walk to Boss Street (Stop T) 0.3km
    10:03-10:18 BOSS STREET (STOP T) board 381 bus towards Waterloo alight at COUNTY
                HALL (STOP G)
          3mins Walk to Westminster Cathedral / Victoria Station (Stop M) 0.2km
    10:29-10:30 WESTMINSTER CATHEDRAL / VICTORIA STATION (STOP M) board 11 bus
                towards Walham Green alight at VICTORIA STATION (STOP G)
         10mins Walk to London SW1A 1AA, UK 0.8km

Display **multiple options** for travelling from **London** to **Edinburgh**, **arriving** by **2pm tomorrow**:

.. code:: shell-session

    $ gdir -M -a 14:00+1 "London" "Edinburgh"

    09:00-13:20 (T) London, UK -> Edinburgh, UK 632km
    09:00-13:20 KING'S CROSS board Lner train towards Edinburgh alight at EDINBURGH
                WAVERLEY
    
    08:30-13:12 (T) London, UK -> Edinburgh, UK 632km
    08:30-13:12 KING'S CROSS board Lner train towards Edinburgh alight at EDINBURGH
                WAVERLEY
    
    08:10-13:29 (TT) London, UK -> Edinburgh, UK 644km
    08:10-11:50 LONDON EUSTON board Avanti West Coast train towards Glasgow Central
                alight at CARLISLE
    12:07-13:29 CARLISLE board Transpennine Express train towards Edinburgh alight
                at EDINBURGH WAVERLEY
    
    08:00-12:20 (T) London, UK -> Edinburgh, UK 632km
    08:00-12:20 KING'S CROSS board Lner train towards Edinburgh alight at EDINBURGH
                WAVERLEY

Display **walking sub-steps** for travelling from **The National Gallery, London** to **Kew Gardens, London**, using any mode of public transport and departing at **2pm** on **15th September this year**:

.. code:: shell-session

    $ gdir -S -d 091514:00 "The National Gallery, London" "Kew Gardens, London"

    14:05-15:11 (UT) Trafalgar Square, London WC2N 5DN, UK -> Royal Botanic Gardens,
                Kew, Richmond TW9, UK 18.3km
          3mins Walk to Charing Cross Station 0.2km
              1 Walk southTake the stairs 69m
              2 Turn right towards Trafalgar Square/A4 24m
              3 Turn left towards Trafalgar Square/A4 48m
              4 Turn right onto Trafalgar Square/A4Destination will be on the left
                4m
              5 Take entrance  29m
    14:08-14:10 CHARING CROSS STATION board Bakerloo underground towards Elephant &
                Castle alight at WATERLOO
          4mins Walk to Waterloo Station 0.2km
              1 Take exit  60m
              2 Take entrance London Waterloo Rail Station 0.1km
    14:20-14:36 WATERLOO STATION board South Western Railway train towards Reading
                alight at RICHMOND
         15mins Walk to Royal Botanic Gardens, Kew, Richmond TW9, UK 1.1km
              1 Take exit Richmond Rail Station 38m
              2 Walk north-east on Kew Rd/A307 towards Sun AlleyGo through 1
                roundabout 1.1km
              3 Turn left 38m
              4 Turn rightDestination will be on the left 11m

**Note**: If you get a *no directions found* error, try appending the city to your origin/destination address. See also the ``-R`` flag below for setting region bias.

**Note 2**: See ``-c`` ``-k`` ``-f`` flags below for setting other transport modes if required (driving, cycling, walking).

Detailed Help and List of Command Line Arguments
------------------------------------------------
.. code::

    usage: gdir [-h] [-b] [-r] [-n] [-m] [-u] [-c | -k | -f]
                [-d time_arg | -a time_arg] [-S] [-M] [-N] [-R region_code] [-C]
                origin destination
    
    Query the Google Directions API and write results to the standard output in
    human-readable format. Uses public transport ('transit') mode by default.
    Requires environment variable GOOGLE_MAPS_API_KEY defining a valid API key.
    Language of directions is determined from locale configuration using
    locale.getdefaultlocale(), which reads from LC_ALL, LC_CTYPE, LANG and
    LANGUAGE in descending order of priority. Word wrapping is achieved using
    shutil.get_terminal_size(), which reads from COLUMNS and which may
    alternatively use system calls to determine the terminal width, using a fall-
    back value of 80 if the terminal width could not be determined. Scripts may
    use the -N flag (see below) to disable word wrapping but should not make
    excessive assumptions about the structure of output: When using the -N flag,
    valid assumptions are 1) routes are delimited by empty lines 2) each route may
    be represented as a two-column table, where rows are separated by newlines and
    where the first and second column in the table are separated by a single space
    3) values in the first column may be left-padded with a variable amount of
    whitespace 4) the format of values in the first column may vary for all rows,
    including the first row 5) route output may be followed by two empty lines,
    followed by travel warnings and/or copyright/transport agency information.
    Status codes: 0 success; 1 generic error; 2 invalid argument; 3
    origin/desination not found; >=4 google-maps-services-python exceptions.
    
    positional arguments:
      origin                start address (quote-enclosed) or latitude,longitude
                            pair
      destination           end address (quote-enclosed) or latitude,longitude
                            pair
    
    optional arguments:
      -h, --help            show this help message and exit
      -b, --bus             prefer to travel by bus
      -r, --rail            prefer to travel by rail (equivalent to train, tram,
                            underground)
      -n, --train           prefer to travel by train
      -m, --tram            prefer to travel by tram
      -u, --underground     prefer to travel by underground (a.k.a. subway)
      -c, --car             travel by car instead of public transport
      -k, --bicycle         travel by bicycle instead of public transport
      -f, --foot            travel on foot instead of public transport
      -d time_arg, --depart time_arg
                            set departure time (see below)
      -a time_arg, --arrive time_arg
                            set arrival time (see below)
      -S, --substeps        show sub-steps in output
      -M, --multiple        show multiple routes, if available
      -N, --no-wrap         disable word wrapping (affects command line mode only;
                            potentially useful for scripting)
      -R region_code, --region region_code
                            set region bias using the specified top-level domain
                            two-character code (ccTLD)
      -C, --copyright       display copyright and transport agency information
                            (see Directions API terms and conditions)
    
    Departure and arrival times are expressed in terms of local time at the origin
    and destination, respectively. Times must be specified in the form
    [[[[cc]yy]mm]dd]HH[:]MM[+N], where ccyy is the year, mm is the month (ranging
    from 1 to 12), dd is the day (ranging from 1 to 31), HH is the hour (ranging
    from 0 to 23) and MM is the minute (ranging from 0 to 59). When left
    unspecified, ccyy, mm and dd values are assumed to be the current year, month
    and day, respectively. For ambiguous times arising from daylight saving
    transitions, it is assumed that the ambiguous time is expressed in the time
    zone's standard time. The suffix +N may be used to offset the specified time
    by N days. Thus, 12:00+1 means 'tomorrow at noon'.
