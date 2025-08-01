get_watershed_monthly_hydrology_by_id_query = """
    SELECT
        results
    FROM
        bcwat_lic.get_monthly_hydrology(:watershed_feature_id, :in_basin, :region_id);
"""
