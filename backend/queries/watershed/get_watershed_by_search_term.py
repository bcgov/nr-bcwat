get_watershed_by_search_term_query = """
    SELECT
        watershed_feature_id as id,
        area_m2,
        longitude,
        latitude,
        COALESCE(gnis_name, 'Unnamed Basin') as name,
        ST_AsGeoJson(upstream_geom_4326_z12)::json as geojson
    FROM
        bcwat_ws.ws_geom_all_report
    WHERE
        watershed_feature_id = %(watershed_feature_id)s
    ORDER BY
        watershed_feature_id
    LIMIT 10;
"""
