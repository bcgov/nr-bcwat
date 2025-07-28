get_watershed_monthly_hydrology_by_id_query = """
    SELECT
        *
    FROM
        bcwat_lic.get_monthly_hydrology(%(watershed_feature_id)s, %(in_basin)s);
"""
