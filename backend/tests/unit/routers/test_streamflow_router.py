import os
import json

def test_get_streamflow_stations(client):
    """
        Unit Test of Streamflow Stations Endpoint
    """
    response = client.get('/streamflow/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/streamflow/router', 'streamflowStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_streamflow_station_report_by_id(client):
    """
        Unit Test of Streamflow report_by_id Endpoint
    """
    response = client.get('/streamflow/stations/107/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_streamflow_station_flow_duration_by_id(client):
    """
        Unit Test of Streamflow Flow Duration by ID Endpoint
    """
    response = client.get('/streamflow/stations/107/report/flow-duration')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}
