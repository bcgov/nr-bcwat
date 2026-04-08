BEGIN;

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Air Quality'
WHERE location_type_code = '01';
-- was: 'Ambient Or Background Air'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Ditch or Culvert'
WHERE location_type_code = '05';
-- was: 'Ditch Or Culvert'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Estuary'
WHERE location_type_code = '07';
-- was: 'Estuarine'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'In-Plant'
WHERE location_type_code = '09';
-- was: 'In Plant'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Lake or Pond'
WHERE location_type_code = '13';
-- was: 'Lake Or Pond'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'River, Stream, or Creek'
WHERE location_type_code = '21';
-- was: 'River,Stream Or Creek'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Seepage or Seepage Pools'
WHERE location_type_code = '23';
-- was: 'Seepage Or Seepage Pools'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Spring or Hot Spring'
WHERE location_type_code = '27';
-- was: 'Spring Or Hot Spring'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Storm Sewer'
WHERE location_type_code = '31';
-- was: 'Stormsewer'

UPDATE bcwat_obs.water_quality_ems_location_type
SET location_type_description = 'Land - Farm'
WHERE location_type_code = '40';
-- was: 'Land Farm'

UPDATE bcwat_obs.network
SET
    network_name = 'BC MoE - Environmental Monitoring Data System',
    licence_link = 'https://www2.gov.bc.ca/gov/content/data/policy-standards/data-policies/open-data/open-government-licence-bc',
    description = 'Data from BC Ministry of Environment Environmental Monitoring Data System, '
                  'acquired via CSV export from DataBC Open Data. '
                  'Contains information licensed under Open Government Licence - British Columbia '
                  '(https://www2.gov.bc.ca/gov/content/data/policy-standards/data-policies/open-data/open-government-licence-bc). '
                  'Any reliance you place upon the information contained here is your sole responsibility '
                  'and strictly at your own risk.'
WHERE network_id = 25;

COMMIT;
