get_watershed_by_search_term_query = """
    SELECT
        watershed_feature_id,
        area_m2,
        longitude,
        latitude,
        COALESCE(gnis_name, 'Unnamed Basin')
    FROM
        bcwat_ws.ws_geom_all_report
    WHERE
        watershed_feature_id::text ILIKE :watershed_feature_id
    ORDER BY
        watershed_feature_id
    LIMIT 10;
"""
