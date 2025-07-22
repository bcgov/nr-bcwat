import os
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
    assert data == load_fixture("climate", "router", "climateStationsResponse.json")

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
    assert data["name"] == load_fixture("climate", "router", "climateStation1Response.json")["name"]
    assert data["nid"] == load_fixture("climate", "router", "climateStation1Response.json")["nid"]
    assert data["net"] == load_fixture("climate", "router", "climateStation1Response.json")["net"]
    assert data["yr"] == load_fixture("climate", "router", "climateStation1Response.json")["yr"]
    assert data["description"] == load_fixture("climate", "router", "climateStation1Response.json")["description"]
    assert data["licence_link"] == load_fixture("climate", "router", "climateStation1Response.json")["licence_link"]
    assert data["temperature"]["current"] == load_fixture("climate", "router", "climateStation1Response.json")["temperature"]["current"]
    assert data["precipitation"] == load_fixture("climate", "router", "climateStation1Response.json")["precipitation"]
    assert data["snow_on_ground_depth"] == load_fixture("climate", "router", "climateStation1Response.json")["snow_on_ground_depth"]
    assert data["snow_water_equivalent"] == load_fixture("climate", "router", "climateStation1Response.json")["snow_water_equivalent"]
    assert data["manual_snow_survey"] == load_fixture("climate", "router", "climateStation1Response.json")["manual_snow_survey"]

    # Handle Snow Depth/SWE Modules
    response = client.get('/climate/stations/287/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    # Provides Explicit Failure, Easier to Debug
    assert data["name"] == load_fixture("climate", "router", "climateStation287Response.json")["name"]
    assert data["nid"] == load_fixture("climate", "router", "climateStation287Response.json")["nid"]
    assert data["net"] == load_fixture("climate", "router", "climateStation287Response.json")["net"]
    assert data["yr"] == load_fixture("climate", "router", "climateStation287Response.json")["yr"]
    assert data["description"] == load_fixture("climate", "router", "climateStation287Response.json")["description"]
    assert data["licence_link"] == load_fixture("climate", "router", "climateStation287Response.json")["licence_link"]
    assert data["temperature"]["current"] == load_fixture("climate", "router", "climateStation287Response.json")["temperature"]["current"]
    assert data["precipitation"] == load_fixture("climate", "router", "climateStation287Response.json")["precipitation"]
    assert data["snow_on_ground_depth"] == load_fixture("climate", "router", "climateStation287Response.json")["snow_on_ground_depth"]
    assert data["snow_water_equivalent"] == load_fixture("climate", "router", "climateStation287Response.json")["snow_water_equivalent"]
    assert data["manual_snow_survey"] == load_fixture("climate", "router", "climateStation287Response.json")["manual_snow_survey"]

    # Handle Manual Snow Survey Modules
    response = client.get('/climate/stations/17401/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    # Provides Explicit Failure, Easier to Debug
    assert data["name"] == load_fixture("climate", "router", "climateStation17401Response.json")["name"]
    assert data["nid"] == load_fixture("climate", "router", "climateStation17401Response.json")["nid"]
    assert data["net"] == load_fixture("climate", "router", "climateStation17401Response.json")["net"]
    assert data["yr"] == load_fixture("climate", "router", "climateStation17401Response.json")["yr"]
    assert data["description"] == load_fixture("climate", "router", "climateStation17401Response.json")["description"]
    assert data["licence_link"] == load_fixture("climate", "router", "climateStation17401Response.json")["licence_link"]
    assert data["temperature"]["current"] == load_fixture("climate", "router", "climateStation17401Response.json")["temperature"]["current"]
    assert data["precipitation"] == load_fixture("climate", "router", "climateStation17401Response.json")["precipitation"]
    assert data["snow_on_ground_depth"] == load_fixture("climate", "router", "climateStation17401Response.json")["snow_on_ground_depth"]
    assert data["snow_water_equivalent"] == load_fixture("climate", "router", "climateStation17401Response.json")["snow_water_equivalent"]
    assert data["manual_snow_survey"] == load_fixture("climate", "router", "climateStation17401Response.json")["manual_snow_survey"]

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
    assert data == load_fixture("climate", "router", "climateStation1Temperature.json")

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
    assert data == load_fixture("climate", "router", "climateStation1Precipitation.json")

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
    assert data == load_fixture("climate", "router", "climateStation1SnowDepth.json")

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
    assert data == load_fixture("climate", "router", "climateStation287SnowWaterEquivalent.json")

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
    print(json.dumps(data, indent=2))
    assert data == load_fixture("climate", "router", "climateStation17401SnowSurvey.json")
