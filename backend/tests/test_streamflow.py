import json

def test_get_streamflow_reports(client):
    """
        Unit Test of Streamflow Reports Endpoint
    """
    response = client.get('/streamflow/reports')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_streamflow_stations(client):
    """
        Unit Test of Streamflow Stations Endpoint
    """
    response = client.get('/streamflow/stations')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

