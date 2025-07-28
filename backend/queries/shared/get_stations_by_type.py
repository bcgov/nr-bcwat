get_stations_by_type_query = """
    SELECT jsonb_build_object(
        'features', jsonb_agg(
          jsonb_build_object(
            'type', 'Feature',
            'properties', jsonb_build_object(
              'id', s.station_id,
              'nid', s.original_id,
              'name', s.station_name,
              'net', n.network_name,
              'ty', st.type_description,
              'yr', ARRAY(
                SELECT sy2.year
                FROM bcwat_obs.station_year sy2
                WHERE sy2.station_id = s.station_id
                GROUP BY sy2.year
                ORDER BY sy2.year
              ),
              'status', ss.status_name,
              'area', s.drainage_area,
              'analysesObj', COALESCE((
                SELECT jsonb_object_agg(variable_id, true)
                FROM (
                  SELECT variable_id
                  FROM bcwat_obs.station_variable
                  WHERE station_id = s.station_id
                    AND variable_id IS NOT NULL
                  GROUP BY variable_id
                ) vars
              ), '{}'::jsonb)
            ),
            'geometry', jsonb_build_object(
              'type', 'Point',
              'coordinates', jsonb_build_array(s.longitude, s.latitude)
            )
          )
        )
      ) AS geojson
    FROM
      bcwat_obs.station s
    LEFT JOIN
      bcwat_obs.station_type st
    USING
      (type_id)
    LEFT JOIN
      bcwat_obs.network n
    USING
      (network_id)
    LEFT JOIN
      bcwat_obs.station_status ss
    ON
      ss.status_id = s.station_status_id
    WHERE
      s.type_id = ANY(%(type_id)s)
"""
