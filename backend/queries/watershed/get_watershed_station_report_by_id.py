get_watershed_station_report_by_id_query = """
    SELECT
        wgar.watershed_feature_id,
        wgar.fwa_watershed_code as watershed_fwa_wc,
        wgar.area_m2 as watershed_area_m2,
        wgar.longitude as watershed_lng,
        wgar.latitude as watershed_lat,
        wgar.gnis_name as watershed_name,
        ST_AsGeoJSON(wgar.upstream_geom_4326_z12, 4326) as watershed_geom_4326,
        frr.watershed_metadata as watershed_metadata,
        wgar2.watershed_feature_id as downstream_id,
        wgar2.fwa_watershed_code as downstream_fwa_wc,
        wgar2.area_m2 as downstream_area_m2,
        wgar2.longitude as downstream_lng,
        wgar2.latitude as downstream_lat,
        wgar2.gnis_name as downstream_name,
        ST_AsGeoJSON(wgar2.upstream_geom_4326_z12, 4326) as downstream_geom_4326,
        fdc.month,
        fdc.month_value,
        fdc_dist.candidate,
        fdc_dist.candidate_month_value,
        fdc_phys.watershed_fdc_data,
        fdc_wsc.original_id as candidate_id,
        fdc_wsc.watershed_feature_id as candidate_wfi,
        fdc_wsc.station_id as candidate_station_id,
        fdc_wsc.station_name as candidate_name,
        fdc_wsc.area_km2 as candidate_area_km2,
        ST_AsGeoJSON(fdc_wsc.geom4326, 4326) as candidate_polygon_4326
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
    JOIN (
        SELECT
            *
        FROM
            bcwat_ws.fdc
        WHERE
            watershed_feature_id = %(watershed_feature_id)s
    ) fdc
    ON
        (wgar.watershed_feature_id = fdc.watershed_feature_id)
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
    JOIN
        bcwat_ws.fdc_wsc_station_in_model fdc_wsc
    ON
        (fdc_dist.candidate = fdc_wsc.original_id)

    WHERE
        wgar.watershed_feature_id = %(watershed_feature_id)s
"""

# SELECT
# 	*
# FROM
# 	bcwat_ws.fund_rollup_report
# JOIN
# 	bcwat_ws.fdc
# USING
# 	(watershed_feature_id)
# JOIN
# 	bcwat_ws.fdc_distance
# USING
# 	(watershed_feature_id)
# JOIN
# 	bcwat_ws.fdc_physical
# USING
# 	(watershed_feature_id)
# JOIN
# 	bcwat_ws.fwa_fund
# USING
# 	(watershed_feature_id)
# LIMIT 1;
