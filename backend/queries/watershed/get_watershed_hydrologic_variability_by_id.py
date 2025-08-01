get_watershed_hydrologic_variability_by_id_query = """
    SELECT
        fdc.month,
        fdc.month_value
    FROM
        bcwat_ws.fdc
    WHERE
        watershed_feature_id = :watershed_feature_id
"""
