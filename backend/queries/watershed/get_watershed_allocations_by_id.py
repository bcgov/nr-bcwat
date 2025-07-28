get_watershed_allocations_by_id_query = """
	SELECT
    	*
    FROM
		bcwat_lic.get_allocs_per_wfi(%(watershed_feature_id)s)
"""
