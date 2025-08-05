import os
import json


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


    response = client.get('/streamflow/stations/107/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}

def test_get_streamflow_station_flow_duration_by_id(client):
    """
        Unit Test of Streamflow Flow Duration by ID Endpoint
    """
    response = client.get('/streamflow/stations/107/report/flow-duration')
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data == {}
