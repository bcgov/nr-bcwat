get_climate_station_csv_by_id_query = """
  SELECT
    so.datestamp,
    so.value,
    so.qa_id,
    v.display_name,
    v.unit
  FROM
    bcwat_obs.station_observation so
  JOIN
		bcwat_obs.variable v
  USING
		(variable_id)
  WHERE
    so.station_id = :station_id
  AND
    so.variable_id IN (5, 6, 7, 8, 16, 27)

  UNION ALL

  SELECT
    cmsp.datestamp,
    cmsp.value,
    cmsp.qa_id,
    v.display_name,
    v.unit
  FROM
    bcwat_obs.climate_msp cmsp
  JOIN
		bcwat_obs.variable v
  USING
		(variable_id)
  WHERE
      cmsp.station_id = :station_id
  ORDER BY
      datestamp ASC;
"""
