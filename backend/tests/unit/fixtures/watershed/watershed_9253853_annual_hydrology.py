
from psycopg2.extras import RealDictRow

annual_hydrology = RealDictRow([ ( 'results',
                { 'allocs_m3s': {'downstream': '0.00131', 'query': '0.00000'},
                  'allocs_m3yr': { 'downstream': '41276.98594',
                                   'query': '0.00000'},
                  'allocs_pct': {'downstream': '< 0.1', 'query': '0'},
                  'area_km2': { 'downstream': '202.220419864881',
                                'query': '19.7687345011687'},
                  'mad_m3s': { 'downstream': '4.73800452825725',
                               'query': '0.633203102699288'},
                  'rr': {'downstream': 'Present', 'query': 'Present'},
                  'runoff_m3yr': { 'downstream': '149520051.700931',
                                   'query': '19982370.233743'},
                  'seasonal_sens': { 'downstream': 'Winter',
                                     'query': 'Winter'}})])
