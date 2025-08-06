get_kwt_hydrologic_variability_by_id_query = """
SELECT
    hydrological_variability
FROM
    bcwat_ws.kwt_hydrological_variability
WHERE
    watershed_feature_id = %(watershed_feature_id)s;
"""
