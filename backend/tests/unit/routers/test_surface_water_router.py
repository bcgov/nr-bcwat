import os
import json

def test_get_surface_water_stations(client):
    """
        Unit Test of Surface Water Stations Endpoint
    """
    response = client.get('/surface-water/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/surface_water/router', 'surfaceWaterStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_surface_water_station_report_by_id(client):
    """
        Unit Test of Surface Water report_by_id Endpoint
    """
    response = client.get('/surface-water/stations/109/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_surface_water_station_statistics(client):
    """
        Very simple endpoint returns 2 data points
    """
    response = client.get('/surface-water/stations/100/station-statistics')
    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['sampleDates'] == 49
    assert data['uniqueParams'] == 20
