import os
import json

def test_get_groundwater_level_stations(client):
    """
        Unit Test of Groundwater Level Stations Endpoint
    """
    response = client.get('/groundwater/level/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater/router', 'groundwaterLevelStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_groundwater_quality_stations(client):
    """
        Unit Test of Groundwater Quality Stations Endpoint
    """
    response = client.get('/groundwater/quality/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater/router', 'groundwaterQualityStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_groundwater_level_station_report_by_id(client):
    """
        Unit Test of Groundwater Level report_by_id Endpoint
    """
    response = client.get('/groundwater/level/stations/103/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}


def test_get_groundwater_quality_station_report_by_id(client):
    """
        Unit Test of Groundwater Quality report_by_id Endpoint
    """
    response = client.get('/groundwater/quality/stations/105/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

