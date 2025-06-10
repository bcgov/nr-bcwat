import json

def test_get_groundwater_level_stations(client):
    """
        Unit Test of Groundwater Level Stations Endpoint
    """
    response = client.get('/groundwater/level/stations')
    assert response.status_code == 200

    from queries.groundwater.get_groundwater_level_stations import get_groundwater_level_stations_query

    data = json.loads(response.data)
    assert data == get_groundwater_level_stations_query

def test_get_groundwater_quality_stations(client):
    """
        Unit Test of Groundwater Quality Stations Endpoint
    """
    response = client.get('/groundwater/quality/stations')
    assert response.status_code == 200

    from queries.groundwater.get_groundwater_quality_stations import get_groundwater_quality_stations_query

    data = json.loads(response.data)
    assert data == get_groundwater_quality_stations_query

def test_get_groundwater_level_station_report_by_id(client):
    """
        Unit Test of Groundwater Level report_by_id Endpoint
    """
    response = client.get('/groundwater/level/stations/103/report')
    assert response.status_code == 200

    from queries.groundwater.get_groundwater_level_station_report_by_id import get_groundwater_level_station_report_by_id_query

    data = json.loads(response.data)
    assert data == get_groundwater_level_station_report_by_id_query

def test_get_groundwater_quality_station_report_by_id(client):
    """
        Unit Test of Groundwater Quality report_by_id Endpoint
    """
    response = client.get('/groundwater/quality/stations/105/report')
    assert response.status_code == 200

    from queries.groundwater.get_groundwater_quality_station_report_by_id import get_groundwater_quality_station_report_by_id_query

    data = json.loads(response.data)
    assert data == get_groundwater_quality_station_report_by_id_query
