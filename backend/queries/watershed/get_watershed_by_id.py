get_watershed_by_id_query = """
	SELECT
		root.watershed_feature_id::TEXT AS wfi,
		ST_AsGeoJson(up.upstream_geom_4326_z12)::json as geojson,
		SUBSTRING(root.fwa_watershed_code, 1, POSITION('-000000' IN root.fwa_watershed_code)-1) AS fwa_code,
		CASE
			WHEN root.lake_name IS NOT null THEN root.lake_name
			WHEN up.gnis_name IS NOT NULL THEN up.gnis_name
			ELSE 'Unnamed Basin'
		END AS name
	FROM
		bcwat_ws.fwa_fund root
	JOIN
		bcwat_ws.ws_geom_all_report up
	ON
		up.watershed_feature_id = root.watershed_feature_id
	WHERE
		root.watershed_feature_id = %(watershed_feature_id)s;
"""
