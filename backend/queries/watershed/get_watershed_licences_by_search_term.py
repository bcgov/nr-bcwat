get_watershed_licences_by_search_term_query = """
    SELECT
        wls_id,
        branding_organization,
        licensee,
        licence_no,
        ann_adjust,
        industry_activity,
        lic_status,
        water_allocation_type,
        purpose,
        purpose_groups,
        licence_term
    FROM
        bcwat_lic.licence_wls_map
    WHERE
        wls_id ILIKE :water_licence_id
    ORDER BY
        wls_id
    LIMIT 10;
"""
