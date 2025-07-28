get_watershed_report_by_id_query = """
  SELECT
        wgar.watershed_feature_id,
        wgar.fwa_watershed_code as watershed_fwa_wc,
        wgar.longitude as watershed_lng,
        wgar.latitude as watershed_lat,
        wgar.gnis_name as watershed_name,
        ST_AsGeoJSON(wgar.upstream_geom_4326_z12, 4326) as watershed_geom_4326,
        frr.watershed_metadata as watershed_metadata,
        fdc_phys.watershed_fdc_data as watershed_fdc_data,
        wgar2.watershed_feature_id as downstream_id,
        frr2.watershed_metadata as downstream_watershed_metadata,
        ST_AsGeoJSON(wgar2.upstream_geom_4326_z12, 4326) as downstream_geom_4326
    FROM
        (
            SELECT
                *
            FROM
                bcwat_ws.ws_geom_all_report
            WHERE
                watershed_feature_id = %(watershed_feature_id)s
        ) wgar
    JOIN
        (
            SELECT
                *
            FROM
                bcwat_ws.fund_rollup_report
            WHERE
                watershed_feature_id = %(watershed_feature_id)s
        ) frr
    USING
        (watershed_feature_id)
    LEFT JOIN
        bcwat_ws.ws_geom_all_report wgar2
    ON
        (frr.downstream_id = wgar2.watershed_feature_id)
    JOIN
    (
        SELECT
            *
        FROM
            bcwat_ws.fdc_physical
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) fdc_phys
    ON
        (wgar.watershed_feature_id = fdc_phys.watershed_feature_id)
    LEFT JOIN
        bcwat_ws.fund_rollup_report frr2
    ON
        (frr2.watershed_feature_id = wgar2.watershed_feature_id)
    WHERE
        wgar.watershed_feature_id = %(watershed_feature_id)s
"""
