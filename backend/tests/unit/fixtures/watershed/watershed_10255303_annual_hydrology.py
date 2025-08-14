
from psycopg2.extras import RealDictRow

annual_hydrology = RealDictRow([ ( 'results',
                { 'allocs_m3s': {'downstream': '0.00000', 'query': '0.00000'},
                  'allocs_m3yr': {'downstream': '0.00000', 'query': '0.00000'},
                  'allocs_pct': {'downstream': '0', 'query': '0'},
                  'area_km2': {'downstream': '87.7', 'query': '18.7'},
                  'mad_m3s': {'downstream': '2.204082', 'query': '0.551000'},
                  'rr': {'downstream': 'None', 'query': 'None'},
                  'runoff_m3yr': { 'downstream': '69555547.772263',
                                   'query': '17388231.799393'},
                  'seasonal_sens': { 'downstream': 'Winter',
                                     'query': 'Winter'}})])
