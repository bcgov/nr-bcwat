get_streamflow_station_report_by_id_query = """
  SELECT
    station_id,
    datestamp,
    variable_id,
    value
  FROM
    bcwat_obs.station_observation
  WHERE
    station_id = %(station_id)s
  AND
    variable_id IN (1, 2)
"""

# The variables above are the metrics of interest for Climate Stations
