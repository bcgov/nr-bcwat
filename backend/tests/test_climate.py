import json

def test_get_climate_reports(client):
    """
        Unit Test of Climate Reports Endpoint
    """
    response = client.get('/climate/reports')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_climate_stations(client):
    """
        Unit Test of Climate Stations Endpoint
    """
    response = client.get('/climate/stations')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

