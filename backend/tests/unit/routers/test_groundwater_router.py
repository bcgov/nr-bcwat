import os
import json

def test_get_groundwater_level_stations(client):
    """
        Unit Test of Groundwater Level Stations Endpoint
    """
    response = client.get('/groundwater/level/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'groundwaterLevelStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_groundwater_quality_stations(client):
    """
        Unit Test of Groundwater Quality Stations Endpoint
    """
    response = client.get('/groundwater/quality/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'groundwaterQualityStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_groundwater_station_statistics(client):
    """
        Very simple endpoint returns 2 data points
    """

    response = client.get('/groundwater/quality/stations/100/station-statistics')
    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['sampleDates'] == 49
    assert data['uniqueParams'] == 20


def test_get_groundwater_level_station_report_by_id(client):
    """
        Unit Test of Groundwater Level report_by_id Endpoint
    """
    response = client.get('/groundwater/level/stations/1/report')
    assert response.status_code == 400

    response = client.get('/groundwater/level/stations/2/report')
    assert response.status_code == 404

    response = client.get('/groundwater/level/stations/16425/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'station16425Response.json')
    with open(path, 'r') as f:
        assert data == json.load(f)


def test_get_groundwater_quality_station_report_by_id(client):
    """
        Unit Test of Groundwater Quality report_by_id Endpoint
    """
    response = client.get('/groundwater/level/stations/1/report')
    assert response.status_code == 400

    response = client.get('/groundwater/level/stations/2/report')
    assert response.status_code == 404

    data = json.loads(response.data)
    assert data == {}

