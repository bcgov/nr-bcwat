get_fwa_query = """
SELECT
    fwa_watershed_code AS fwa_watershed_code
FROM
    bcwat_ws.ws_geom_all_report
WHERE
    watershed_feature_id = %(watershed_feature_id)s;
"""
