get_streamflow_station_csv_by_id_query = """
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
    so.variable_id IN (1, 2)
"""
