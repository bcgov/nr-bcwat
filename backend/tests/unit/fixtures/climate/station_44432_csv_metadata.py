
from psycopg2.extras import RealDictRow

csv_metadata = RealDictRow([ ('id', 44432),
              ('name', 'Haines Apps No 2'),
              ('net', 21),
              ('nid', '1203315'),
              ('latitude', 59.516667),
              ('longitude', -136.466667),
              ('description', None),
              ('area', None),
              ('elevation', 478.0),
              ('network_name', 'Environment Canada'),
              ( 'network_description',
                'Data from Environment Canada has been acquired from The '
                'Meteorological Service of Canada and Pacific Climate Impacts '
                'Consortium '
                "(http://www.pacificclimate.org/data/bc-station-data). PCIC's "
                'terms of use are: https://pacificclimate.org/terms-of-use. '
                'This data is a copy of an official work that is published by '
                'the Government of Canada and the reproduction has not been '
                'produced in affiliation with or with the endorsement of the '
                'Government of Canada. For more information on the terms and '
                'conditions of the data please see: '
                'http://www.ec.gc.ca/default.asp?lang=En&n=12345678-1&xsl=mainhomeitem&xml=5830C36B-1773-4E3E-AF8C-B21F54633E0A '
                'and http://weather.gc.ca/mainmenu/disclaimer_e.html. Any '
                'reliance you place upon the information contained here is '
                'your sole responsibility and strictly at your own risk. In no '
                'event will the original data custodian, BC Oil and Gas '
                'Commission, Ministry of Forests, Lands and Natural Resource '
                'Operations or Foundry Spatial Ltd. be liable for any loss or '
                'damage whatsoever, including without limitation, indirect or '
                'consequential loss or damage, arising from reliance upon the '
                'data or derived information.'),
              ('status_name', 'Historical'),
              ('start_yr', 1955),
              ('end_yr', 1974)])
