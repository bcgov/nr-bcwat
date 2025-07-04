get_groundwater_level_station_report_by_id_query = """
    SELECT
      gwl.station_id,
      gwl.datestamp,
      gwl.variable_id,
      gwl.value
    FROM
      bcwat_obs.ground_water_level gwl
    WHERE
      gwl.station_id = %(station_id)s
"""
