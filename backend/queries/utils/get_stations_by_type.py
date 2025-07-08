get_stations_by_type_query = """
    SELECT
      s.station_id as id,
      s.station_name as name,
      n.network_name as net,
      s.original_id as nid,
      s.latitude,
      s.longitude,
      st.type_description as ty,
      s.drainage_area as area,
      ss.status_name as status,
      sy.year as yr,
      sv.variable_id
    FROM
      bcwat_obs.station s
    JOIN
      bcwat_obs.station_year sy
    USING
      (station_id)
    JOIN
      bcwat_obs.station_type st
    USING
      (type_id)
    JOIN
      bcwat_obs.network n
    USING
      (network_id)
    JOIN
      bcwat_obs.station_status ss
    ON
      (ss.status_id = s.station_status_id)
    LEFT JOIN
      bcwat_obs.station_variable sv
    USING
      (station_id)
    WHERE
      s.type_id = %(type_id)s
"""
