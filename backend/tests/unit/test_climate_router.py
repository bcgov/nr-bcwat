import os
import json

def test_get_climate_stations(client):
    """
        Unit Test of Climate Stations Endpoint
    """
    response = client.get('/climate/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), 'fixtures/climate/router', 'climateStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_climate_station_report_by_id(client):
    """
        Unit Test of Climate report_by_id Endpoint
    """
    response = client.get('/climate/stations/101/report')
    assert response.status_code == 200


    data = json.loads(response.data)
    assert data == {}
