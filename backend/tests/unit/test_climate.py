import json

def test_get_climate_stations(client):
    """
        Unit Test of Climate Stations Endpoint
    """
    response = client.get('/climate/stations')
    assert response.status_code == 200

    from queries.climate.get_climate_stations import get_climate_stations_query

    data = json.loads(response.data)
    assert data == get_climate_stations_query

def test_get_climate_station_report_by_id(client):
    """
        Unit Test of Climate report_by_id Endpoint
    """
    response = client.get('/climate/stations/101/report')
    assert response.status_code == 200

    from queries.climate.get_climate_station_report_by_id import get_climate_station_report_by_id_query
    data = json.loads(response.data)

    assert data == get_climate_station_report_by_id_query
