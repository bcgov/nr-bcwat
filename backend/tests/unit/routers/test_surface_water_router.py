import os
import json

from freezegun import freeze_time

def test_get_surface_water_stations(client):
    """
        Unit Test of Surface Water Stations Endpoint
    """
    response = client.get('/surface-water/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/surface_water', 'surfaceWaterStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

@freeze_time('2025-08-07')
def test_get_surface_water_station_report_by_id(client):
    """
        Unit Test of Surface Water report_by_id Endpoint
    """
    response = client.get('/surface-water/stations/41773/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/surface_water', 'station41773Response.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_surface_water_station_statistics(client):
    """
        Very simple endpoint returns 2 data points
    """
    response = client.get('/surface-water/stations/100/station-statistics')
    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['sampleDates'] == 49
    assert data['uniqueParams'] == 20

def test_get_surface_water_station_csv_by_id(client):
    response = client.get('/surface-water/stations/1/csv')
    assert response.status_code == 400

    data = json.loads(response.data)
    assert data == {
        "name": None,
        "nid": None,
        "net": None,
        "description": None,
        "licence_link": None
    }

    # Will only return station metadata, not a csv
    response = client.get('/surface-water/stations/2/csv')
    assert response.status_code == 404

    data = json.loads(response.data)
    assert data == {
        "name" :"unit_test",
        "nid" : 1,
        "net" : "test_network",
        "description": "I am a unit test",
        "licence_link": "unit_test.com/unit"
    }

    response = client.get('/surface-water/stations/41773/csv')
    assert response.status_code == 200

    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    data = response.data.decode('utf-8')
    path = os.path.join(os.path.dirname(__file__), '../fixtures/surface_water', 'station_41773.csv')
    with open(path, 'r') as f:
        assert data + '\n' == f.read()
