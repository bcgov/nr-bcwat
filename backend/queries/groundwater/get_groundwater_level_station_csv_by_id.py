get_groundwater_level_station_csv_by_id_query = """
  SELECT
    so.datestamp,
    v.display_name,
    so.value,
    so.qa_id
  FROM
    bcwat_obs.station_observation so
  JOIN
		bcwat_obs.variable v
  USING
		(variable_id)
  WHERE
    so.station_id = %(station_id)s
  AND
    so.variable_id IN (3)
"""
