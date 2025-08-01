import json
from tests.unit.test_utils import load_fixture

def test_get_climate_stations(client):
    """
        Unit Test of Climate Stations Endpoint - Return Data

        Validate Data Returned
    """
    response = client.get('/climate/stations')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["type"] == "FeatureCollection"
    assert data["features"] == load_fixture("climate", "getClimateStationsResponse.json")['geojson']['features']

def test_get_climate_stations_none(client, mock_features_none):
    """
        Unit Test of Climate Stations Endpoint - Empty Features

        Validate Data Returned
    """
    response = client.get('/climate/stations')
    assert response.status_code == 200

    data = response.get_json()
    assert data == {
        'type': 'FeatureCollection',
        'features': []
    }

def test_get_climate_station_report_by_id(client):
    """
        Unit Test of Climate report_by_id Endpoint
    """

    # ID does not correspond to Climate Station
    response = client.get('/climate/stations/0/report')
    assert response.status_code == 400

    # ID Correspond to Climate Station but has no metrics
    response = client.get('/climate/stations/47421/report')
    assert response.status_code == 404

    response = client.get('/climate/stations/47538/report')
    assert response.status_code == 500
    data = json.loads(response.data)

    assert data['message'] == 'Error Calculating Metrics for Climate Station: Blueberry (Id: 47538)'

    # Handle Temperature/Precipitation Modules
    response = client.get('/climate/stations/1/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    # Provides Explicit Failure, Easier to Debug
    expected_response = load_fixture("climate", "climateStation1Response.json")
    assert data["name"] == expected_response["name"]
    assert data["nid"] == expected_response["nid"]
    assert data["net"] == expected_response["net"]
    assert data["yr"] == expected_response["yr"]
    assert data["description"] == expected_response["description"]
    assert data["licence_link"] == expected_response["licence_link"]
    assert data["temperature"]["current"] == expected_response["temperature"]["current"]
    assert data["precipitation"] == expected_response["precipitation"]
    assert data["snow_on_ground_depth"] == expected_response["snow_on_ground_depth"]
    assert data["snow_water_equivalent"] == expected_response["snow_water_equivalent"]
    assert data["manual_snow_survey"] == expected_response["manual_snow_survey"]

    # Handle Snow Depth/SWE Modules
    response = client.get('/climate/stations/287/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    # Provides Explicit Failure, Easier to Debug
    expected_response = load_fixture("climate", "climateStation287Response.json")
    assert data["name"] == expected_response["name"]
    assert data["nid"] == expected_response["nid"]
    assert data["net"] == expected_response["net"]
    assert data["yr"] == expected_response["yr"]
    assert data["description"] == expected_response["description"]
    assert data["licence_link"] == expected_response["licence_link"]
    assert data["temperature"]["current"] == expected_response["temperature"]["current"]
    assert data["precipitation"] == expected_response["precipitation"]
    assert data["snow_on_ground_depth"] == expected_response["snow_on_ground_depth"]
    assert data["snow_water_equivalent"] == expected_response["snow_water_equivalent"]
    assert data["manual_snow_survey"] == expected_response["manual_snow_survey"]

    # Handle Manual Snow Survey Modules
    response = client.get('/climate/stations/17401/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    # Provides Explicit Failure, Easier to Debug
    expected_response = load_fixture("climate", "climateStation17401Response.json")
    assert data["name"] == expected_response["name"]
    assert data["nid"] == expected_response["nid"]
    assert data["net"] == expected_response["net"]
    assert data["yr"] == expected_response["yr"]
    assert data["description"] == expected_response["description"]
    assert data["licence_link"] == expected_response["licence_link"]
    assert data["temperature"]["current"] == expected_response["temperature"]["current"]
    assert data["precipitation"] == expected_response["precipitation"]
    assert data["snow_on_ground_depth"] == expected_response["snow_on_ground_depth"]
    assert data["snow_water_equivalent"] == expected_response["snow_water_equivalent"]
    assert data["manual_snow_survey"] == expected_response["manual_snow_survey"]

def test_get_climate_station_report_temperature_by_id_and_year(client):
    """
        Unit Test of Climate Get Station Report by Id and Year
    """
    response = client.get('/climate/stations/47421/report/temperature/2020')
    assert response.status_code == 404

    response = client.get('/climate/stations/47538/report/temperature/2020')
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data['message'] == 'Error Calculating Yearly Temperature Metrics for Climate Station Id: 47538'

    response = client.get('/climate/stations/1/report/temperature/1985')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == load_fixture("climate", "climateStation1Temperature.json")

def test_get_climate_station_report_precipitation_by_id_and_year(client):
    """
        Unit Test of Climate Get Station Report by Id and Year
    """
    response = client.get('/climate/stations/47421/report/precipitation/2020')
    assert response.status_code == 404

    response = client.get('/climate/stations/47538/report/precipitation/2020')
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data['message'] == 'Error Calculating Yearly Precipitation Metrics for Climate Station Id: 47538'

    response = client.get('/climate/stations/1/report/precipitation/1985')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == load_fixture("climate", "climateStation1Precipitation.json")

def test_get_climate_station_report_snow_depth_by_id_and_year(client):
    """
        Unit Test of Climate Get Station Report by Id and Year
    """
    response = client.get('/climate/stations/47421/report/snow-depth/2020')
    assert response.status_code == 404

    response = client.get('/climate/stations/47538/report/snow-depth/2020')
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data['message'] == 'Error Calculating Yearly Snow Depth Metrics for Climate Station Id: 47538'

    response = client.get('/climate/stations/1/report/snow-depth/1984')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == load_fixture("climate", "climateStation1SnowDepth.json")

def test_get_climate_station_report_snow_water_equivalent_by_id_and_year(client):
    """
        Unit Test of Climate Get Station Report by Id and Year
    """
    response = client.get('/climate/stations/47421/report/snow-water-equivalent/2020')
    assert response.status_code == 404

    response = client.get('/climate/stations/47538/report/snow-water-equivalent/2020')
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data['message'] == 'Error Calculating Yearly Snow Water Equivalent Metrics for Climate Station Id: 47538'

    response = client.get('/climate/stations/287/report/snow-water-equivalent/1994')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == load_fixture("climate", "climateStation287SnowWaterEquivalent.json")

def test_get_climate_station_report_snow_survey_by_id_and_year(client):
    """
        Unit Test of Climate Get Station Report by Id and Year
    """
    response = client.get('/climate/stations/47421/report/snow-survey/2020')
    assert response.status_code == 404

    response = client.get('/climate/stations/47538/report/snow-survey/2020')
    assert response.status_code == 500

    data = json.loads(response.data)
    assert data['message'] == 'Error Calculating Yearly Manual Snow Survey Metrics for Climate Station Id: 47538'

    response = client.get('/climate/stations/17401/report/snow-survey/1989')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == load_fixture("climate", "climateStation17401SnowSurvey.json")
