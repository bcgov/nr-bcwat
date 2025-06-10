import json

def test_get_surface_water_stations(client):
    """
        Unit Test of Surface Water Stations Endpoint
    """
    response = client.get('/surface-water/stations')
    assert response.status_code == 200

    from queries.surface_water.get_surface_water_stations import get_surface_water_stations_query

    data = json.loads(response.data)
    assert data == get_surface_water_stations_query

def test_get_surface_water_station_report_by_id(client):
    """
        Unit Test of Surface Water report_by_id Endpoint
    """
    response = client.get('/surface-water/stations/109/report')
    assert response.status_code == 200

    from queries.surface_water.get_surface_water_station_report_by_id import get_surface_water_station_report_by_id_query

    data = json.loads(response.data)
    assert data == get_surface_water_station_report_by_id_query
