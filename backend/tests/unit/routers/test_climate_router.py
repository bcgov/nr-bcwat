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
    response = client.get('/climate/stations/101/report')
    assert response.status_code == 200


    data = json.loads(response.data)
    assert data == {}
