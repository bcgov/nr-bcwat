import json

def test_get_streamflow_stations(client):
    """
        Unit Test of Streamflow Stations Endpoint
    """
    response = client.get('/streamflow/stations')
    assert response.status_code == 200

    from queries.streamflow.get_streamflow_stations import get_streamflow_stations_query

    data = json.loads(response.data)
    assert data == get_streamflow_stations_query

def test_get_streamflow_station_report_by_id(client):
    """
        Unit Test of Streamflow report_by_id Endpoint
    """
    response = client.get('/streamflow/stations/107/report')
    assert response.status_code == 200

    from queries.streamflow.get_streamflow_station_report_by_id import get_streamflow_station_report_by_id_query

    data = json.loads(response.data)
    assert data == get_streamflow_station_report_by_id_query

def test_get_streamflow_station_flow_duration_by_id(client):
    """
        Unit Test of Streamflow Flow Duration by ID Endpoint
    """
    response = client.get('/streamflow/stations/107/report/flow-duration')
    assert response.status_code == 200

    from queries.streamflow.get_streamflow_station_report_flow_duration_by_id import get_streamflow_station_report_flow_duration_by_id_query

    data = json.loads(response.data)
    assert data == get_streamflow_station_report_flow_duration_by_id_query
