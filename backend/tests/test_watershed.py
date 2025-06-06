import json

def test_get_watershed_reports(client):
    """
        Unit Test of Watershed Reports Endpoint
    """
    response = client.get('/watershed/reports')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_watershed_stations(client):
    """
        Unit Test of Watershed Stations Endpoint
    """
    response = client.get('/watershed/stations')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

