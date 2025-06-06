import json

def test_get_surface_water_reports(client):
    """
        Unit Test of Surface Water Reports Endpoint
    """
    response = client.get('/surface-water/reports')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_surface_water_stations(client):
    """
        Unit Test of Surface Water Stations Endpoint
    """
    response = client.get('/surface-water/stations')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

