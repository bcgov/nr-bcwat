get_streamflow_station_historical_values_by_id_query = """
    SELECT
        datestamp,
        value
    FROM
        bcwat_obs.station_observation
    WHERE
        station_id = %(station_id)s
    AND
        variable_id = 1;
"""
