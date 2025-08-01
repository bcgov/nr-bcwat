get_groundwater_level_station_report_by_id_query = """
    SELECT
      station_id,
      datestamp,
      variable_id,
      value
    FROM
      bcwat_obs.station_observation
    WHERE
      station_id = :station_id
    AND
      variable_id = 3
"""
# The variable above is the metric of interest for Ground Water Level Stations
