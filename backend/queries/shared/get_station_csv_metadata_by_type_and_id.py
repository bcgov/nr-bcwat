get_station_csv_metadata_by_type_and_id_query = """
   SELECT
      s.station_id as id,
      s.station_name as name,
      s.network_id as net,
      s.original_id as nid,
      s.latitude,
      s.longitude,
      s.station_description as description,
      s.drainage_area as area,
      s.elevation,
      n.network_name,
      n.description as network_description,
      ss.status_name,
      MIN(sy.year) as start_yr,
      MAX(sy.year) as end_yr
    FROM
      bcwat_obs.station s
    JOIN
      bcwat_obs.station_year sy
    USING
      (station_id)
    JOIN
      bcwat_obs.station_status ss
    ON
		(s.station_status_id = ss.status_id)
    JOIN
      bcwat_obs.network n
    USING
      (network_id)
    WHERE
      s.type_id = ANY(%(type_id)s)
    AND
      s.station_id = %(station_id)s
    AND
      s.prov_terr_state_loc = 'BC'
    GROUP BY
      s.station_id,
      s.station_name,
      s.network_id,
      s.original_id,
      s.latitude,
      s.longitude,
      s.station_description,
      s.drainage_area,
			n.network_name,
			n.description,
			ss.status_name
"""
