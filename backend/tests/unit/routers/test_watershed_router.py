import os
import json

def test_get_watershed_by_lat_lng(client):
    """
        Unit Test of get Watershed by Lat/Lng endpoint
    """
    response = client.get('/watershed/')
    assert response.status_code == 400

    response = client.get('/watershed/?lat=1')
    assert response.status_code == 400

    response = client.get('/watershed/?lng=1')
    assert response.status_code == 400

    response = client.get('/watershed/?lng=nonFloat&lng=nonFloat')
    assert response.status_code == 400

def test_get_watershed_licenses(client):
    """
        Unit Test of get Watershed Licenses endpoint
    """
    response = client.get('/watershed/licences')
    assert response.status_code == 200
    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/watershed', 'watershedLicenses.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        assert data == expected_data

def test_get_watershed_licenses_by_search_term(client):
    """
        Search endpoint, requires more thoughtful testing
    """
    # No input, return 400
    response = client.get('/watershed/licences/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == "Missing required query parameters 'licence_no'"

    # 404, nothing found
    response = client.get('/watershed/licences/search?licence_no=404')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['results'] == []

    # 200, data found
    response = client.get('/watershed/licences/search?licence_no=200')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['results'] == [1,2,3]

def test_get_place_by_name(client):
    """
        Search endpoint, requires more thoughtful testing
    """
    # No input, return 400
    response = client.get('/watershed/location/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == "Missing required query parameters 'location_name'"

    # 404, nothing found
    response = client.get('/watershed/location/search?location_name=404')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['results'] == []

    # 200, data found
    response = client.get('/watershed/location/search?location_name=200')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['results'] == [1,2,3]

def test_get_watersheds_by_search_term(client):
    """
        Get the given watersheds by the search term
    """
    response = client.get('/watershed/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == "Missing required query parameters 'wfi'"

    # 404, nothing found
    response = client.get('/watershed/search?wfi=404')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['results'] ==[]

    # 200, data found
    response = client.get('/watershed/search?wfi=200')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['results'] == [1, 2, 3]

def test_get_watershed_by_id(client):
    """
        Similar to the above, like a search but is an exact match
    """
    # 404, nothing found
    response = client.get('/watershed/404')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['wfi'] is None
    assert data['geojson'] is None
    assert data['name'] is None

    # 200, data found
    response = client.get('/watershed/200')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['wfi'] == 1
    assert data['geojson'] == {"type" : "FeatureCollection"}
    assert data['name'] == "unit_test"


def test_get_watershed_station_report_by_id(client):
    """
        Unit Test of Watershed report_by_id Endpoint

        Going to do a test for each of the regions used (Kootenay, Cariboo, Omineca and Northwest)
    """
    # KWT - wfi = 9253853
    response = client.get('/watershed/9253853/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/watershed', 'watershed9253853ReportData.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        assert data == expected_data

    # Cariboo - wfi = 9191927
    response = client.get('/watershed/9191927/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/watershed', 'watershed9191927ReportData.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        assert data == expected_data

    # Omineca - wfi = 10255303
    response = client.get('/watershed/10255303/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/watershed', 'watershed10255303ReportData.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        assert data == expected_data

    # Northwest - wfi = 9196070
    response = client.get('/watershed/9196070/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/watershed', 'watershed9196070ReportData.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        assert data == expected_data

def test_get_watershed_polygon_by_id(client):
    # Error since the format is unacceptible
    response = client.get("/watershed/101/report/download_watershed/gdb")
    assert response.status_code == 404
    data = json.loads(response.data)
    data["error"] == "The format value was an unexpected value."

    # Error Case due to db failure
    response = client.get("/watershed/404/report/download_watershed/geojson")
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data["message"] == "Error getting the watershed polygon. Please try again later"

    # Test when geojson is requested
    response = client.get("/watershed/101/report/download_watershed/geojson")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/zip"
    assert response.headers["Content-Disposition"] == "attachment; filename=101.zip"

    # Test when shapefile is requested
    response = client.get("/watershed/101/report/download_watershed/shapefile")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/zip"
    assert response.headers["Content-Disposition"] == "attachment; filename=101.zip"
