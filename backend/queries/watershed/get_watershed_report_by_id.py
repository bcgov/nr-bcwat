get_watershed_report_by_id_query = """
    SELECT
        *
    FROM (
        SELECT
            *
        FROM
            bcwat_ws.fund_rollup_report
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) frr
    JOIN (
        SELECT
            *
        FROM
            bcwat_ws.fdc
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) fdc
    USING (watershed_feature_id)
    JOIN
    (
        SELECT
            *
        FROM
            bcwat_ws.fdc_distance
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) fdc_dist
    USING
        (watershed_feature_id)
    JOIN
    (
        SELECT
            *
        FROM
            bcwat_ws.fdc_physical
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) fdc_phys
    USING
        (watershed_feature_id)
    JOIN
    (
        SELECT
            *
        FROM
            bcwat_ws.fwa_fund
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) fwa
    USING
        (watershed_feature_id)
    JOIN
    (
        SELECT
            *
        FROM
            bcwat_ws.ws_geom_all_report
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) wgar
    USING
        (watershed_feature_id)
"""
