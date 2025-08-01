get_climate_station_report_by_id_query = """
  SELECT
    'non_msp_observation' AS source,
    so.station_id,
    so.datestamp,
    so.variable_id,
    so.value,
	  NULL::date as survey_period
  FROM
    bcwat_obs.station_observation so
  WHERE
    so.station_id = :station_id
  AND
    so.variable_id IN (5, 6, 8, 16, 27)

  UNION ALL

  SELECT
      'msp' AS source,
      cmsp.station_id,
      cmsp.datestamp,
      cmsp.variable_id,
      cmsp.value,
      cmsp.survey_period
  FROM
      bcwat_obs.climate_msp cmsp
  WHERE
      cmsp.station_id = :station_id
  ORDER BY
      datestamp ASC;
"""
# The variables in the first SELECT are the metrics of interest for Climate Stations
