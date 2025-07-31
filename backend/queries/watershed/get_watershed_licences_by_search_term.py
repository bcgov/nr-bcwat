get_watershed_licences_by_search_term_query = """
    SELECT
        wls_id,
        licensee,
        licence_no,
        ann_adjust,
        licence_term,
        longitude,
        latitude
    FROM
        bcwat_lic.licence_wls_map
    WHERE
        wls_id ILIKE %(water_licence_id)s
    ORDER BY
        wls_id
    LIMIT 10;
"""
