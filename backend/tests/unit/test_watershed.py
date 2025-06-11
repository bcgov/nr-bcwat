import json

def test_get_watershed_stations(client):
    """
        Unit Test of Watershed Stations Endpoint
    """
    response = client.get('/watershed/stations')
    assert response.status_code == 200

    from queries.watershed.get_watershed_stations import get_watershed_stations_query

    data = json.loads(response.data)
    assert data == get_watershed_stations_query

def test_get_watershed_station_report_by_id(client):
    """
        Unit Test of Watershed report_by_id Endpoint
    """
    response = client.get('/watershed/stations/111/report')
    assert response.status_code == 200

    from queries.watershed.get_watershed_station_report_by_id import get_watershed_station_report_by_id_query

    data = json.loads(response.data)
    assert data == get_watershed_station_report_by_id_query
