import datetime

from psycopg2.extras import RealDictRow

csv_metadata = RealDictRow([ ('id', 32555),
              ('name', 'Stanley Creek'),
              ('net', 24),
              ('nid', '4E03'),
              ('latitude', 59.89627),
              ('longitude', -136.8984),
              ('description', None),
              ('area', None),
              ('elevation', 767.0),
              ('network_name', 'BC ENV - Manual Snow Survey'),
              ( 'network_description',
                'Data from BC Ministry of Environment Manual Snow Survey has '
                'been acquired from Ministry of Environment and Climate Change '
                'Strategy and DataBC. Any reliance you place upon the '
                'information contained here is your sole responsibility and '
                'strictly at your own risk. In no event will the original data '
                'custodian, BC Oil and Gas Commission, Ministry of Forests, '
                'Lands and Natural Resource Operations or Foundry Spatial Ltd. '
                'be liable for any loss or damage whatsoever, including '
                'without limitation, indirect or consequential loss or damage, '
                'arising from reliance upon the data or derived information.'),
              ('status_name', 'Historical'),
              ('start_yr', 1977),
              ('end_yr', 1986)])
