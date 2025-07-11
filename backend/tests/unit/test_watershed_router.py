import os
import json

def test_get_watershed_by_lat_lng(client):
    """
        Unit Test of get Watershed by Lat/Lng endpoint
    """
    response = client.get('/watershed/')
    assert response.status_code == 400

    response = client.get('/watershed/?lat=1')
    assert response.status_code == 400

    response = client.get('/watershed/?lng=1')
    assert response.status_code == 400

    response = client.get('/watershed/?lng=nonFloat&lng=nonFloat')
    assert response.status_code == 400

def test_get_watershed_stations(client):
    """
        Unit Test of Watershed Stations Endpoint
    """
    response = client.get('/watershed/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), 'fixtures/watershed/router', 'watershedStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_watershed_station_report_by_id(client):
    """
        Unit Test of Watershed report_by_id Endpoint
    """
    response = client.get('/watershed/stations/111/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}
