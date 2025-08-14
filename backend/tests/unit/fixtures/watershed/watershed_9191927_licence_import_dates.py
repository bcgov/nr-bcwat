import datetime

from psycopg2.extras import RealDictRow

licence_import_dates = [ RealDictRow([ ('dataset', 'licence_ogc_short_term_approvals'),
                ('import_date', datetime.date(2025, 7, 30))]),
  RealDictRow([ ('dataset', 'licence_wls_bc'),
                ('import_date', datetime.date(2025, 7, 29))]),
  RealDictRow({'dataset': 'hydat', 'import_date': datetime.date(2025, 8, 11)}),
  RealDictRow([ ('dataset', 'wls_water_approvals'),
                ('import_date', datetime.date(2025, 8, 12))]),
  RealDictRow([ ('dataset', 'water_rights_applications_public'),
                ('import_date', datetime.date(2025, 8, 12))]),
  RealDictRow([ ('dataset', 'water_rights_licences_public'),
                ('import_date', datetime.date(2025, 8, 12))])]
