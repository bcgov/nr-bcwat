get_streamflow_station_flow_metrics_by_id_query = """
    SELECT
        *
    FROM
        bcwat_obs.flow_metric
    WHERE
        station_id = :station_id
"""
