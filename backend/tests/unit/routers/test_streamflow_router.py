import os
import json

from freezegun import freeze_time

def test_get_streamflow_stations(client):
    """
        Unit Test of Streamflow Stations Endpoint
    """
    response = client.get('/streamflow/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/streamflow/router', 'streamflowStationsResponse.json')
    with open(path, 'r') as f:
        assert data['type'] == 'FeatureCollection'
        assert data['features'] == json.load(f)['geojson']['features']

@freeze_time('2025-08-06')
def test_get_streamflow_station_report_by_id(client):
    """
        Unit Test of Streamflow report_by_id Endpoint
    """
    # station 1 mocked to not have data
    response = client.get('/streamflow/stations/1/report')
    assert response.status_code == 400

    data = json.loads(response.data)
    # Ensure we get our default empty response
    assert data['name'] is None
    assert data['nid'] is None
    assert data['net'] is None
    assert data['yr'] is None
    assert data['ty'] is None
    assert data['description'] is None
    assert data['licence_link'] is None
    assert data['sevenDayFlow'] == {}
    assert data['monthlyMeanFlow'] == {}
    assert data['stage'] == {}
    assert data['flowDurationTool'] == {}
    assert data['flowMetrics'] == {}
    assert not data['hasStationMetrics']
    assert not data['hasFlowMetrics']
    assert data['meanAnnualFlow'] is None

    # This station only has stage (Primary Water Level)
    response = client.get('/streamflow/stations/42373/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/streamflow', 'stationReport42373Response.json')
    with open(path, 'r') as f:
        assert data == json.load(f)


    # This station only has flow (Preliminary Discharge)
    response = client.get('/streamflow/stations/47214/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/streamflow', 'stationReport47214Response.json')
    with open(path, 'r') as f:
        expected_response = json.load(f)
        assert data['description'] == expected_response['description']
        assert data['flowDurationTool'] == expected_response['flowDurationTool']
        assert data['flowMetrics'] == expected_response['flowMetrics']
        assert data['hasFlowMetrics'] == expected_response['hasFlowMetrics']
        assert data['hasStationMetrics'] == expected_response['hasStationMetrics']
        assert data['licence_link'] == expected_response['licence_link']
        assert round(data['meanAnnualFlow'], 5) == round(expected_response['meanAnnualFlow'], 5)
        index = 0
        for val in data['monthlyMeanFlow']['terms']:
            for k in val.keys():
                if(k != 'term'):
                    assert round(val[k], 5) == round(expected_response['monthlyMeanFlow']['terms'][index][k], 5)
                else:
                    assert val[k] == expected_response['monthlyMeanFlow']['terms'][index][k]
            index += 1

    # This station has both flow and stage
    response = client.get('/streamflow/stations/42648/report')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/streamflow', 'stationReport42648Response.json')
    with open(path, 'r') as f:
        expected_response = json.load(f)
        assert data['description'] == expected_response['description']
        assert data['flowDurationTool'] == expected_response['flowDurationTool']
        assert data['flowMetrics'] == expected_response['flowMetrics']
        assert data['hasFlowMetrics'] == expected_response['hasFlowMetrics']
        assert data['hasStationMetrics'] == expected_response['hasStationMetrics']
        assert data['licence_link'] == expected_response['licence_link']
        assert round(data['meanAnnualFlow'], 5) == round(expected_response['meanAnnualFlow'], 5)
        index = 0
        for val in data['monthlyMeanFlow']['terms']:
            for k in val.keys():
                if(k != 'term'):
                    assert round(val[k], 5) == round(expected_response['monthlyMeanFlow']['terms'][index][k], 5)
                else:
                    assert val[k] == expected_response['monthlyMeanFlow']['terms'][index][k]
            index += 1


def test_get_streamflow_station_csv_by_id(client):
    """
        Unit Test of Streamflow Flow Duration by ID Endpoint
    """
    # Mocked to not return any data
    response = client.get('/streamflow/stations/1/csv')
    assert response.status_code == 400

    data = json.loads(response.data)
    assert data == {
        "name": None,
        "nid": None,
        "net": None,
        "description": None,
        "licence_link": None
    }

    # Will only return station metadata, not a csv
    response = client.get('/streamflow/stations/2/csv')
    assert response.status_code == 404

    data = json.loads(response.data)
    assert data == {
        "name" :"unit_test",
        "nid" : 1,
        "net" : "test_network",
        "description": "I am a unit test",
        "licence_link": "unit_test.com/unit"
    }

    response = client.get('/streamflow/stations/32509/csv')
    assert response.status_code == 200

    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    data = response.data.decode('utf-8')
    path = os.path.join(os.path.dirname(__file__), '../fixtures/streamflow', 'station_32509.csv')
    with open(path, 'r') as f:
        assert data + '\n' == f.read()
