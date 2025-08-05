get_watershed_by_lat_lng_query = """
	WITH pt AS
	(
		SELECT
			ST_SetSRID(ST_Point(%(lng)s::numeric, %(lat)s::numeric), 4326) AS loc
	)
	SELECT
		root.watershed_feature_id::TEXT AS wfi,
		ST_AsGeoJson(up.upstream_geom_4326_z12)::json as geojson,
		SUBSTRING(root.fwa_watershed_code, 1, POSITION('-000000' IN root.fwa_watershed_code)-1) AS fwa_code,
		CASE
			WHEN root.lake_name IS NOT null THEN root.lake_name
			WHEN up.gnis_name IS NOT NULL THEN up.gnis_name
			WHEN p.gnis_name IS NOT null THEN p.gnis_name
			ELSE 'Unnamed Basin'
		END AS name
	FROM
		bcwat_ws.fwa_fund root
	JOIN
		(
			SELECT
				CASE
			WHEN ST_Closestpoint(streams.geom4326, pt.loc) IS NULL THEN pt.loc
			ELSE ST_Closestpoint(streams.geom4326, pt.loc)
		END AS pt_on_line_geom,
				streams.gnis_name
			FROM
				pt
			LEFT JOIN
				bcwat_ws.fwa_stream_name streams
			ON
				ST_DWithin(streams.geom4326, pt.loc, 0.01)
			ORDER BY
				stream_magnitude desc, ST_Distance(streams.geom4326, pt.loc) ASC
			LIMIT 1
		) p
	ON
		ST_Intersects(p.pt_on_line_geom, root.geom4326)
	JOIN
		bcwat_ws.ws_geom_all_report up
	ON
		up.watershed_feature_id = root.watershed_feature_id
	WHERE
		root.in_study_area
	LIMIT 1;
"""
