
from psycopg2.extras import RealDictRow

annual_hydrology = RealDictRow([ ( 'results',
                { 'allocs_m3s': {'downstream': '0.00000', 'query': '0.00000'},
                  'allocs_m3yr': {'downstream': '0.00000', 'query': '0.00000'},
                  'allocs_pct': {'downstream': '0', 'query': '0'},
                  'area_km2': {'downstream': '8.9', 'query': '6.4'},
                  'mad_m3s': {'downstream': '0.307492', 'query': '0.217501'},
                  'rr': {'downstream': 'None', 'query': 'None'},
                  'runoff_m3yr': { 'downstream': '9703713.611789',
                                   'query': '6863803.727038'},
                  'seasonal_sens': { 'downstream': 'Summer',
                                     'query': 'Summer'}})])
