import json

def test_get_groundwater_level_reports(client):
    """
        Unit Test of Groundwater Level Reports Endpoint
    """
    response = client.get('/groundwater/level/reports')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_groundwater_level_stations(client):
    """
        Unit Test of Groundwater Level Stations Endpoint
    """
    response = client.get('/groundwater/level/stations')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_groundwater_quality_reports(client):
    """
        Unit Test of Groundwater Quality Reports Endpoint
    """
    response = client.get('/groundwater/quality/reports')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_groundwater_quality_stations(client):
    """
        Unit Test of Groundwater Quality Stations Endpoint
    """
    response = client.get('/groundwater/quality/stations')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

