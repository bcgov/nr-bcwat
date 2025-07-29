get_climate_station_csv_by_id_query = """
  SELECT
    'non_msp_observation' AS source,
    so.station_id,
    so.datestamp,
    so.variable_id,
    v.display_name,
    so.value,
    so.qa_id,
		NULL::date as survey_period
  FROM
    bcwat_obs.station_observation so
  JOIN
		bcwat_obs.variable v
  USING
		(variable_id)
  WHERE
    so.station_id = %(station_id)s
  AND
    so.variable_id IN (5, 6, 7, 8, 16, 27)

  UNION ALL

  SELECT
    'msp' AS source,
    cmsp.station_id,
    cmsp.datestamp,
    cmsp.variable_id,
    v.display_name,
    cmsp.value,
    cmsp.qa_id,
    cmsp.survey_period
  FROM
    bcwat_obs.climate_msp cmsp
  JOIN
		bcwat_obs.variable v
  USING
		(variable_id)
  WHERE
      cmsp.station_id = %(station_id)s
  ORDER BY
      datestamp ASC;
"""
