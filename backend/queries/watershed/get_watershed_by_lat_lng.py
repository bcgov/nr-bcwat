get_watershed_by_lat_lng_query = """
    WITH pt AS
	(
		SELECT
			ST_Transform(ST_SetSRID(ST_Point(120, 120), 4326), 3005) AS loc
	)
	SELECT
		ff.watershed_feature_id_foundry::TEXT AS wfi,
		geom_geojson4326::JSON AS geom,
		SUBSTRING(ff.fwa_watershed_code, 1, POSITION('-000000' IN ff.fwa_watershed_code)-1) AS fwa_code,
		CASE
			WHEN ff.lake_name IS NOT null THEN ff.lake_name
			WHEN up.gnis_name IS NOT NULL THEN up.gnis_name
			WHEN p.gnis_name IS NOT null THEN p.gnis_name
			ELSE 'Unnamed Basin'
		END AS name
	FROM
		bcwat_ws.fwa_funds ff
	JOIN
			(
				SELECT
					CASE
				WHEN ST_Closestpoint(streams.geom, pt.loc) IS NULL THEN pt.loc
				ELSE ST_Closestpoint(streams.geom, pt.loc)
			END AS pt_on_line_geom,
					streams.gnis_name
				FROM
					pt
				LEFT JOIN
					base.fwa_stream_names streams
				ON
					ST_DWithin(streams.geom, pt.loc, search_distance::numeric)
				ORDER BY
					stream_magnitude desc, ST_Distance(streams.geom, pt.loc) ASC
				LIMIT 1
			) p
		ON
			ST_Intersects(p.pt_on_line_geom, ff.the_geom)
		JOIN
			bcwat_ws.ws_geoms_all_report up
		ON
			up.watershed_feature_id = ff.watershed_feature_id_foundry
		WHERE ff.in_study_area
		LIMIT 1;
"""
