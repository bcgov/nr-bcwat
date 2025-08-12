
from psycopg2.extras import RealDictRow

annual_hydrology = RealDictRow([ ( 'results',
                { 'allocs_m3s': {'downstream': '0.00000', 'query': '0.00000'},
                  'allocs_m3yr': {'downstream': '0.00000', 'query': '0.00000'},
                  'allocs_pct': {'downstream': '0', 'query': '0'},
                  'area_km2': { 'downstream': '1.44511348789269',
                                'query': '1.44511348789269'},
                  'mad_m3s': { 'downstream': '0.0296109307256357',
                               'query': '0.0296109307256357'},
                  'rr': {'downstream': 'Present', 'query': 'Present'},
                  'runoff_m3yr': { 'downstream': '934449.90746732',
                                   'query': '934449.90746732'},
                  'seasonal_sens': { 'downstream': 'Winter',
                                     'query': 'Winter'}})])
