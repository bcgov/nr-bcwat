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
        geom AS geom4326,
        latitude,
        longitude,
        is_consumptive
    FROM datas;
"""

bc_wls_wrl_wra = """
    SELECT
        fs_id as wls_wrl_wra_id,
        licence_no
        tpod_tag,
        purpose,
        pcl_no,
        qty_original,
        qty_flag,
        qty_units,
        licensee,
        lic_status_date,
        priority_date,
        expiry_date,
        longitude,
        latitude,
        stream_name,
        quantity_day_m3,
        quantity_sec_m3,
        quantity_ann_m3,
        lic_status,
        rediversion_flag,
        flag_desc,
        file_no,
        water_allocation_type,
        pod_diversion_type,
        geom AS geom4326,
        water_source_type_desc,
        hydraulic_connectivity,
        well_tag_number,
        related_licences,
        industry_activity,
        purpose_groups,
        is_consumptive,
        ann_adjust,
        NULL::DOUBLE PRECISION AS quantity_ann_m3_storage_adjust,
        puc_groupings_storage,
        qty_diversion_max_rate,
        qty_units_diversion_max_rate
    FROM
        water_licences.bc_wls_wrl_wra;
"""

licence_bc_purpose = """
    SELECT
        purpose,
        general_activity_code,
        purpose_name,
        purpose_code,
        purpose_groups,
        is_consumptive,
        puc_groupings_storage,
        pid,
        still_used_by_databc
    FROM
        water_licences.licence_bc_purpose;
"""

wls_water_approvals_deanna = """
    SELECT
        appfileno,
        proponent,
        podno,
        latitude,
        longitude,
        purpose,
        sourcetype,
        sourcename,
        fishpresence,
        startdate,
        expirationdate,
        ms,
        md,
        my,
        geom AS geom4326,
        fs_id AS deanna_id,
        quantity,
        quantity_units,
        qty_diversion_max_rate,
        qty_units_diversion_max_rate,
        approval_status
    FROM
        water_licences.wls_water_approvals_deanna;
"""

bc_water_approvals = """
    SELECT
        fs_id AS bc_wls_water_approval_id,
        wsd_region,
        approval_type,
        approval_file_number,
        fcbc_tracking_number,
        source,
        works_description,
        quantity,
        quantity_units,
        qty_diversion_max_rate,
        qty_units_diversion_max_rate,
        water_district,
        precinct,
        latitude,
        longitude,
        approval_status,
        application_date,
        fcbc_acceptance_date,
        approval_issuance_date,
        approval_start_date,
        approval_expiry_date,
        approval_refuse_abandon_date,
        ST_Transform(geom, 4326) AS geom4326,
        created,
        proponent,
        podno
    FROM
        water_licences.wls_water_approvals;
"""

water_management_geoms = """
    SELECT
        gid AS district_id,
        district_n AS district_name,
        ST_Transform(geom, 4326) AS geom4326
    FROM
        water_licences.watmgmt_dist_area_svw;
"""

licence_bc_app_land = """
    SELECT
        licence_no,
        appurtenant_land,
        related_licences,
        fa,
        purpose
    FROM
        water_licences.licence_bc_app_land;
"""

bc_data_import_date = """
    SELECT
        dataset,
        import_date
    FROM
        water_licences.import_date
    WHERE
        dataset IN ('water_rights_applications_public', 'water_rights_licences_public', 'wls_water_approvals', 'licence_wls_bc', 'licence_ogc_short_term_approvals');
"""

elevation_bookend = """
    SELECT
        8 AS region_id,
        elevs_flat AS elevation_flat,
        elevs_steep AS elevation_steep
    FROM
        owt.elevs_bookends
    UNION
    SELECT
        7 AS region_id,
        elevs_flat AS elevation_flat,
        elevs_steep AS elevation_steep
    FROM
        nwwt.elevs_bookends;
"""

lakes_licence_query = """
    SELECT
        fs_id AS lake_licence_id,
        waterbody_poly_id,
        lake_name,
        licence_stream_name
    FROM owt.lakes_licence
    UNION
    SELECT
        fs_id AS lake_licence_id,
        waterbody_poly_id,
        lake_name,
        licence_stream_name
    FROM nwwt.lakes_licence
    UNION
    SELECT
        fs_id AS lake_licence_id,
        waterbody_poly_id,
        lake_name,
        licence_stream_name
    FROM kwt.lakes_licence;
"""
