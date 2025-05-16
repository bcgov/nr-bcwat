licence_ogc_short_term_approvals = """
    WITH datas AS (
        SELECT * FROM cariboo.licence_ogc_short_term_approvals
        UNION
        SELECT * FROM kwt.licence_ogc_short_term_approvals
        UNION
        SELECT * FROM nwwt.licence_ogc_short_term_approvals
        UNION
        SELECT * FROM owt.licence_ogc_short_term_approvals
    )
    SELECT
        fs_id AS short_term_approval_id,
        pod_number,
        short_term_water_use_num,
        water_source_type,
        water_source_type_desc,
        water_source_name,
        purpose,
        purpose_desc,
        approved_volume_per_day,
        approved_total_volume,
        approved_start_date,
        approved_end_date,
        status,
        application_determination_num,
        activity_approval_date,
        activity_cancel_date,
        legacy_ogc_file_number,
        proponent,
        authority_type,
        land_type,
        data_source,
        geom,
        latitude,
        longitude,
        is_consumptive,
        qty_display
    FROM datas;
"""
