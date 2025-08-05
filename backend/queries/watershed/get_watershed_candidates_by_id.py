get_watershed_candidates_by_id_query = """
    SELECT
        fdc_dist.candidate,
        fdc_dist.candidate_month_value,
        fdc_wsc.original_id as candidate_id,
        fdc_wsc.watershed_feature_id as candidate_wfi,
        fdc_wsc.station_id as candidate_station_id,
        fdc_wsc.station_name as candidate_name,
        fdc_wsc.area_km2 as candidate_area_km2,
        ST_AsGeoJSON(fdc_wsc.geom4326, 4326) as candidate_polygon_4326,
        fdc_phys.watershed_fdc_data as candidate_climate_data
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
    LEFT JOIN
        bcwat_ws.fund_rollup_report frr2
    ON
        (frr.downstream_id = frr2.watershed_feature_id)
    JOIN
    (
        SELECT
            *
        FROM
            bcwat_ws.fdc_distance
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) fdc_dist
    ON
        (wgar.watershed_feature_id = fdc_dist.watershed_feature_id)
    JOIN
        bcwat_ws.fdc_wsc_station_in_model fdc_wsc
    ON
        (fdc_dist.candidate = fdc_wsc.original_id)
    JOIN
        bcwat_ws.fdc_physical fdc_phys
    ON
        (fdc_wsc.watershed_feature_id = fdc_phys.watershed_feature_id)
    WHERE
        wgar.watershed_feature_id = %(watershed_feature_id)s
"""
