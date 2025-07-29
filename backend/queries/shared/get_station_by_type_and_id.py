get_station_by_type_and_id = """
    SELECT
      s.station_id as id,
      s.station_name as name,
      s.network_id as net,
      s.original_id as nid,
      s.latitude,
      s.longitude,
      s.station_description as description,
      st.type_description as ty,
      s.drainage_area as area,
      n.licence_link,
      ARRAY_AGG(sy.year) as yr
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
    WHERE
      s.type_id = ANY(%(type_id)s)
    AND
      s.station_id = %(station_id)s
    GROUP BY
      s.station_id,
      s.station_name,
      s.network_id,
      s.original_id,
      s.latitude,
      s.longitude,
      s.station_description,
      st.type_description,
      s.drainage_area,
      n.licence_link
"""
