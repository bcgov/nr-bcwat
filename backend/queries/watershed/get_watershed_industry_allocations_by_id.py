get_watershed_industry_allocations_by_id_query = """
    SELECT
        *
    FROM
        bcwat_lic.get_allocs_by_industry(%(watershed_feature_id)s);
"""
