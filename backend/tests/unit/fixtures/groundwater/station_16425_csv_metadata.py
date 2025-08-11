
from psycopg2.extras import RealDictRow

csv_metadata = RealDictRow([ ('id', 16425),
              ('name', 'Golden (Highway 95 & Almberg Rd.)'),
              ('net', 10),
              ('nid', '309'),
              ('latitude', 51.259258),
              ('longitude', -116.918664),
              ( 'description',
                'Observation Well 309 was included in the network in 1989. It '
                'is located in surficial aquifer 450,  a  IIB  aquifer south '
                'of Golden. It was established to monitor water levels in '
                'developed aquifers.  '),
              ('area', None),
              ('elevation', None),
              ('network_name', 'BC MoE - Groundwater Observation Well Network'),
              ( 'network_description',
                'Data from BC Ministry of Environment Groundwater Observation '
                'Well Network has been acquired from Ministry of Environment '
                '(http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/) '
                'and contains information licensed under Open Government '
                'License '
                '(http://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/databc/open-data/open-government-license-bc). '
                'Any reliance you place upon the information contained here is '
                'your sole responsibility and strictly at your own risk. In no '
                'event will BC Oil and Gas Commission, BC Ministry of '
                'Environment or Foundry Spatial Ltd. be liable for any loss or '
                'damage whatsoever, including without limitation, indirect or '
                'consequential loss or damage, arising from reliance upon the '
                'data or derived information.'),
              ('status_name', 'Active, Real-time, Responding'),
              ('start_yr', 1989),
              ('end_yr', 2025)])
