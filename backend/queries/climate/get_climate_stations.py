get_climate_stations_query = """
    SELECT
      s.station_id as id,
      s.station_name as name,
      s.network_id as net,
      s.original_id as nid,
      s.latitude,
      s.longitude,
      s.type_id as ty,
      s.drainage_area as area,
      sy.year as yr
    FROM
      bcwat_obs.station s
    JOIN
      bcwat_obs.station_year sy
    USING
      (station_id)
"""
