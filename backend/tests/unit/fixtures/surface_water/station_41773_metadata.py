import datetime

from psycopg2.extras import RealDictRow

station_metadata = RealDictRow([ ('id', 41773),
              ( 'name',
                'Windy Craggy WC-6 Up Gradient of Falls to Tats Glacier'),
              ('net', 25),
              ('nid', 'E316742'),
              ('latitude', 59.72374),
              ('longitude', -137.737455),
              ( 'description',
                'Site WC-6 Red Creek up gradient of waterfall into Tats '
                'Glacier. Part of Windy Craggy Surface Sampling Project. '
                'Tatshenshini-Alsek  BC Parks. See Windy Craggy Exploration '
                'Site BC Can: 2016 Mon Report on Ecocat'),
              ('ty', 'Water Quality Surface Water'),
              ('area', None),
              ( 'licence_link',
                'http://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/databc/open-data/open-government-license-bc'),
              ('yr', [2016])])
