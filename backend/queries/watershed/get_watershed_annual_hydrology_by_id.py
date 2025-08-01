get_watershed_annual_hydrology_by_id_query = """
    SELECT
        results
    FROM
        bcwat_lic.get_annual_hydrology(:watershed_feature_id);
"""
