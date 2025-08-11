import os
import json

def test_get_groundwater_level_stations(client):
    """
        Unit Test of Groundwater Level Stations Endpoint
    """
    response = client.get('/groundwater/level/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'groundwaterLevelStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_groundwater_quality_stations(client):
    """
        Unit Test of Groundwater Quality Stations Endpoint
    """
    response = client.get('/groundwater/quality/stations')
    assert response.status_code == 200

    data = json.loads(response.data)

    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'groundwaterQualityStationsResponse.json')
    with open(path, 'r') as f:
        assert data == json.load(f)

def test_get_groundwater_station_statistics(client):
    """
        Very simple endpoint returns 2 data points
    """

    response = client.get('/groundwater/quality/stations/100/station-statistics')
    assert response.status_code == 200

    data = json.loads(response.data)

    assert data['sampleDates'] == 49
    assert data['uniqueParams'] == 20


def test_get_groundwater_level_station_report_by_id(client):
    """
        Unit Test of Groundwater Level report_by_id Endpoint
    """
    response = client.get('/groundwater/level/stations/1/report')
    assert response.status_code == 400

    response = client.get('/groundwater/level/stations/2/report')
    assert response.status_code == 404

    response = client.get('/groundwater/level/stations/16425/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'station16425Response.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        for key in data.keys():
            if(key == "monthly_mean_flow"):
                terms = data[key]['terms']
                for index in range(len(terms)):
                    for term_key in terms[index].keys():
                        if(term_key != 'term'):
                            assert round(float(terms[index][term_key]), 5) == round(float(expected_data[key]['terms'][index][term_key]), 5)
            else:
                assert data[key] == expected_data[key]


def test_get_groundwater_level_station_report_by_id_and_year(client):
    """
        Unit Test of Groundwater Level Hydrograph
    """
    response = client.get('/groundwater/level/stations/2/report/hydrograph/2020')
    assert response.status_code == 404

    response = client.get('/groundwater/level/stations/16425/report/hydrograph/2020')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'station16425Hydrograph.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        assert data == expected_data

def test_get_groundwater_quality_station_report_by_id(client):
    """
        Get for groundwater quality station report
    """
    response = client.get('/groundwater/quality/stations/1/report')
    assert response.status_code == 400

    response = client.get('/groundwater/quality/stations/2/report')
    assert response.status_code == 404

    response = client.get('/groundwater/quality/stations/15045/report')
    assert response.status_code == 200

    data = json.loads(response.data)
    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'station15045Response.json')
    with open(path, 'r') as f:
        expected_data = json.load(f)
        for key in data.keys():
            assert data[key] == expected_data[key]

def test_get_groundwater_level_station_csv_by_id(client):
    """
        Generates csv from raw data
    """
    response = client.get('/groundwater/level/stations/1/csv')
    assert response.status_code == 400

    response = client.get('/groundwater/level/stations/2/csv')
    assert response.status_code == 404

    response = client.get('/groundwater/level/stations/16425/csv')
    assert response.status_code == 200

    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    data = response.data.decode('utf-8')
    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'station_16425.csv')
    with open(path, 'r') as f:
        assert data + '\n' == f.read()

def test_get_groundwater_quality_station_csv_by_id(client):
    """
        Generates csv from raw data
    """
    response = client.get('/groundwater/quality/stations/1/csv')
    assert response.status_code == 400

    response = client.get('/groundwater/quality/stations/2/csv')
    assert response.status_code == 404

    response = client.get('/groundwater/quality/stations/15045/csv')
    assert response.status_code == 200

    assert response.headers["Content-Type"] == "text/csv; charset=utf-8"
    data = response.data.decode('utf-8')
    path = os.path.join(os.path.dirname(__file__), '../fixtures/groundwater', 'station_15045.csv')

    with open(path, 'r') as f:
        assert data + '\n' == f.read()
