import json
from utils.watershed import (
    build_climate_chart_data,
    unpack_candidate_metadata,
    generate_hydrologic_variability,
    generate_future_hydrologic_variability,
    post_process_bus_stops,
    build_fwa_list
)
import pytest
from constants import WILLISTON_FWA

def test_build_climate_chart_data():
    """
        Test building the climate chart data. Simple reformatting data function
    """
    # Simple case of reformatting
    watershed_metadata = {
        "watershed_metadata": {
            "tave_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            "tave_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            "tave_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            "ppt_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            "ppt_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            "ppt_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            "pas_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            "pas_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            "pas_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12]
        }
    }

    response = build_climate_chart_data(watershed_metadata)
    assert response['temperature']['historical'] == [1,2,3,4,5,6,7,8,9,10,11,12]
    assert response['temperature']['future'] == [{"min": i+1, "max": i+1} for i in range(12)]
    assert response['precipitation']['historical'] == [1,2,3,4,5,6,7,8,9,10,11,12]
    assert response['precipitation']['future'] == [{"min": i+1, "max": i+1} for i in range(12)]
    assert response['snow']['historical'] == [1,2,3,4,5,6,7,8,9,10,11,12]
    assert response['snow']['future'] == [{"min": i+1, "max": i+1} for i in range(12)]

    # Fill null behavior
    watershed_metadata = {
        "watershed_metadata": {
            # Nothing in here!!!
            # "tave_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "tave_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "tave_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "ppt_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "ppt_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "ppt_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "pas_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "pas_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "pas_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12]
        }
    }

    response = build_climate_chart_data(watershed_metadata)
    assert response['temperature']['historical'] == [None] * 12
    assert response['temperature']['future'] == [{"min": None, "max": None}] * 12
    assert response['precipitation']['historical'] == [None] * 12
    assert response['precipitation']['future'] == [{"min": None, "max": None}] * 12
    assert response['snow']['historical'] == [None] * 12
    assert response['snow']['future'] == [{"min": None, "max": None}] * 12

def test_unpack_candidate_metadata():
    """
        Format the shape of a DB response, simple function
    """
    # Empty input
    query_metadata = {
        'watershed_feature_id': None,
        'watershed_name': None,
        'watershed_lat': None,
        'watershed_lng': None,
        'watershed_fdc_data': {
            'upstream_area_km2': None,
            'min_elev': None,
            'avg_elev': None,
            'max_elev': None,
            'month': None,
            'ppt': None,
            'pas': None,
            'tave': None
        }
    }

    candidate_metadata = []

    response = unpack_candidate_metadata(query_metadata, candidate_metadata)

    assert response['hydrologicVariabilityMiniMapGeoJson'] == []
    assert response['hydrologicVariabilityDistanceValues'] == []
    climate_data = response['hydrologicVariabilityClimateData'][0]
    assert climate_data['type'] == 'query'
    assert climate_data['station_number'] is None
    assert climate_data['station_name'] is None
    assert climate_data['lat'] is None
    assert climate_data['lng'] is None
    assert climate_data['area_km2'] is None
    assert climate_data['min_elev'] is None
    assert climate_data['avg_elev'] is None
    assert climate_data['max_elev'] is None
    assert climate_data['month'] is None
    assert climate_data['ppt'] is None
    assert climate_data['pas'] is None
    assert climate_data['tave'] is None

    query_metadata = {
        'watershed_feature_id': 1,
        'watershed_name': 'unit_test',
        'watershed_lat': 0,
        'watershed_lng': 0,
        'watershed_fdc_data': {
            'upstream_area_km2': 100,
            'min_elev': 0,
            'avg_elev': 1,
            'max_elev': 2,
            'month': [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12],
            'ppt': [1,1,1,1,1,1,1,1,1,1,1,1],
            'pas': [1,1,1,1,1,1,1,1,1,1,1,1],
            'tave': [1,1,1,1,1,1,1,1,1,1,1,1]
        }
    }

    candidate_metadata = [
        {
            'candidate': 1,
            'candidate_id': 1,
            'candidate_polygon_4326': json.dumps({'type': 'FeatureCollection'}),
            'candidate_month_value': {
                    'month01': 1,
                    'month02': 1,
                    'month03': 1,
                    'month04': 1,
                    'month05': 1,
                    'month06': 1,
                    'month07': 1,
                    'month08': 1,
                    'month09': 1,
                    'month10': 1,
                    'month11': 1,
                    'month12': 1
                },
            'candidate_station_id': 1,
            'candidate_name': 'tester',
            'candidate_climate_data':{
                'avg_elev': 1,
                'lat': 0,
                'lon': 0,
                'max_elev': 2,
                'min_elev': 0,
                'month': [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12],
                'pas': [1,1,1,1,1,1,1,1,1,1,1,1],
                'ppt': [1,1,1,1,1,1,1,1,1,1,1,1],
                'tave': [1,1,1,1,1,1,1,1,1,1,1,1],
                'upstream_area_km2': 1
            }
        }
    ]

    result = unpack_candidate_metadata(query_metadata, candidate_metadata)

    assert result['hydrologicVariabilityMiniMapGeoJson'] == [{'candidate': 1, 'geom': {'type': 'FeatureCollection'}}]
    distance = result['hydrologicVariabilityDistanceValues'][0]
    assert distance['month01'] == 1
    assert distance['month02'] == 1
    assert distance['month03'] == 1
    assert distance['month04'] == 1
    assert distance['month05'] == 1
    assert distance['month06'] == 1
    assert distance['month07'] == 1
    assert distance['month08'] == 1
    assert distance['month09'] == 1
    assert distance['month10'] == 1
    assert distance['month11'] == 1
    assert distance['month12'] == 1
    query_climate_data = result['hydrologicVariabilityClimateData'][0]
    assert query_climate_data['type'] == 'query'
    assert query_climate_data['station_number'] == 1
    assert query_climate_data['station_name'] == 'unit_test'
    assert query_climate_data['lat'] == 0
    assert query_climate_data['lng'] == 0
    assert query_climate_data['area_km2'] == 100
    assert query_climate_data['min_elev'] == 0
    assert query_climate_data['avg_elev'] == 1
    assert query_climate_data['max_elev'] == 2
    assert query_climate_data['month'] == [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12]
    assert query_climate_data['ppt'] == [1] * 12
    assert query_climate_data['pas'] == [1] * 12
    assert query_climate_data['tave'] == [1] * 12

    candidate_climate_data = result['hydrologicVariabilityClimateData'][1]
    assert candidate_climate_data['type'] == 'candidate'
    assert candidate_climate_data['station_number'] == 1
    assert candidate_climate_data['station_name'] == 'tester'
    assert candidate_climate_data['lat'] == 0
    assert candidate_climate_data['lng'] == 0
    assert candidate_climate_data['area_km2'] == 1
    assert candidate_climate_data['min_elev'] == 0
    assert candidate_climate_data['avg_elev'] == 1
    assert candidate_climate_data['max_elev'] == 2
    assert candidate_climate_data['month'] == [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12]
    assert candidate_climate_data['ppt'] == [1] * 12
    assert candidate_climate_data['pas'] == [1] * 12
    assert candidate_climate_data['tave'] == [1] * 12


    # Multiple candidates
    query_metadata = {
        'watershed_feature_id': 1,
        'watershed_name': 'unit_test',
        'watershed_lat': 0,
        'watershed_lng': 0,
        'watershed_fdc_data': {
            'upstream_area_km2': 100,
            'min_elev': 0,
            'avg_elev': 1,
            'max_elev': 2,
            'month': [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12],
            'ppt': [1,1,1,1,1,1,1,1,1,1,1,1],
            'pas': [1,1,1,1,1,1,1,1,1,1,1,1],
            'tave': [1,1,1,1,1,1,1,1,1,1,1,1]
        }
    }

    candidate_metadata = [
        {
            'candidate': 1,
            'candidate_id': 1,
            'candidate_polygon_4326': json.dumps({'type': 'FeatureCollection'}),
            'candidate_month_value': {
                    'month01': 1,
                    'month02': 1,
                    'month03': 1,
                    'month04': 1,
                    'month05': 1,
                    'month06': 1,
                    'month07': 1,
                    'month08': 1,
                    'month09': 1,
                    'month10': 1,
                    'month11': 1,
                    'month12': 1
                },
            'candidate_station_id': 1,
            'candidate_name': 'tester',
            'candidate_climate_data':{
                'avg_elev': 1,
                'lat': 0,
                'lon': 0,
                'max_elev': 2,
                'min_elev': 0,
                'month': [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12],
                'pas': [1,1,1,1,1,1,1,1,1,1,1,1],
                'ppt': [1,1,1,1,1,1,1,1,1,1,1,1],
                'tave': [1,1,1,1,1,1,1,1,1,1,1,1],
                'upstream_area_km2': 1
            }
        },
        {
            'candidate': 2,
            'candidate_id': 2,
            'candidate_polygon_4326': json.dumps({'type': 'FeatureCollection'}),
            'candidate_month_value': {
                    'month01': 1,
                    'month02': 1,
                    'month03': 1,
                    'month04': 1,
                    'month05': 1,
                    'month06': 1,
                    'month07': 1,
                    'month08': 1,
                    'month09': 1,
                    'month10': 1,
                    'month11': 1,
                    'month12': 1
                },
            'candidate_station_id': 2,
            'candidate_name': 'tester_2',
            'candidate_climate_data':{
                'avg_elev': 1,
                'lat': 0,
                'lon': 0,
                'max_elev': 2,
                'min_elev': 0,
                'month': [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12],
                'pas': [1,1,1,1,1,1,1,1,1,1,1,1],
                'ppt': [1,1,1,1,1,1,1,1,1,1,1,1],
                'tave': [1,1,1,1,1,1,1,1,1,1,1,1],
                'upstream_area_km2': 1
            }
        },{
            'candidate': 3,
            'candidate_id': 3,
            'candidate_polygon_4326': json.dumps({'type': 'FeatureCollection'}),
            'candidate_month_value': {
                    'month01': 1,
                    'month02': 1,
                    'month03': 1,
                    'month04': 1,
                    'month05': 1,
                    'month06': 1,
                    'month07': 1,
                    'month08': 1,
                    'month09': 1,
                    'month10': 1,
                    'month11': 1,
                    'month12': 1
                },
            'candidate_station_id': 3,
            'candidate_name': 'tester_3',
            'candidate_climate_data':{
                'avg_elev': 1,
                'lat': 0,
                'lon': 0,
                'max_elev': 2,
                'min_elev': 0,
                'month': [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12],
                'pas': [1,1,1,1,1,1,1,1,1,1,1,1],
                'ppt': [1,1,1,1,1,1,1,1,1,1,1,1],
                'tave': [1,1,1,1,1,1,1,1,1,1,1,1],
                'upstream_area_km2': 1
            }
        }
    ]

    result = unpack_candidate_metadata(query_metadata, candidate_metadata)

    assert result['hydrologicVariabilityMiniMapGeoJson'] == [
        {'candidate': 1, 'geom': {'type': 'FeatureCollection'}},
        {'candidate': 2, 'geom': {'type': 'FeatureCollection'}},
        {'candidate': 3, 'geom': {'type': 'FeatureCollection'}}
    ]
    distance = result['hydrologicVariabilityDistanceValues'][0]
    for distance in result['hydrologicVariabilityDistanceValues']:
        assert distance['month01'] == 1
        assert distance['month02'] == 1
        assert distance['month03'] == 1
        assert distance['month04'] == 1
        assert distance['month05'] == 1
        assert distance['month06'] == 1
        assert distance['month07'] == 1
        assert distance['month08'] == 1
        assert distance['month09'] == 1
        assert distance['month10'] == 1
        assert distance['month11'] == 1
        assert distance['month12'] == 1
    query_climate_data = result['hydrologicVariabilityClimateData'][0]
    assert query_climate_data['type'] == 'query'
    assert query_climate_data['station_number'] == 1
    assert query_climate_data['station_name'] == 'unit_test'
    assert query_climate_data['lat'] == 0
    assert query_climate_data['lng'] == 0
    assert query_climate_data['area_km2'] == 100
    assert query_climate_data['min_elev'] == 0
    assert query_climate_data['avg_elev'] == 1
    assert query_climate_data['max_elev'] == 2
    assert query_climate_data['month'] == [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12]
    assert query_climate_data['ppt'] == [1] * 12
    assert query_climate_data['pas'] == [1] * 12
    assert query_climate_data['tave'] == [1] * 12

    candidate_climate_data = result['hydrologicVariabilityClimateData'][1]
    assert candidate_climate_data['type'] == 'candidate'
    assert candidate_climate_data['station_number'] == 1
    assert candidate_climate_data['station_name'] == 'tester'
    assert candidate_climate_data['lat'] == 0
    assert candidate_climate_data['lng'] == 0
    assert candidate_climate_data['area_km2'] == 1
    assert candidate_climate_data['min_elev'] == 0
    assert candidate_climate_data['avg_elev'] == 1
    assert candidate_climate_data['max_elev'] == 2
    assert candidate_climate_data['month'] == [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12]
    assert candidate_climate_data['ppt'] == [1] * 12
    assert candidate_climate_data['pas'] == [1] * 12
    assert candidate_climate_data['tave'] == [1] * 12

    candidate_2_climate_data = result['hydrologicVariabilityClimateData'][2]
    assert candidate_2_climate_data['type'] == 'candidate'
    assert candidate_2_climate_data['station_number'] == 2
    assert candidate_2_climate_data['station_name'] == 'tester_2'
    assert candidate_2_climate_data['lat'] == 0
    assert candidate_2_climate_data['lng'] == 0
    assert candidate_2_climate_data['area_km2'] == 1
    assert candidate_2_climate_data['min_elev'] == 0
    assert candidate_2_climate_data['avg_elev'] == 1
    assert candidate_2_climate_data['max_elev'] == 2
    assert candidate_2_climate_data['month'] == [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12]
    assert candidate_2_climate_data['ppt'] == [1] * 12
    assert candidate_2_climate_data['pas'] == [1] * 12
    assert candidate_2_climate_data['tave'] == [1] * 12

    candidate_3_climate_data = result['hydrologicVariabilityClimateData'][3]
    assert candidate_3_climate_data['type'] == 'candidate'
    assert candidate_3_climate_data['station_number'] == 3
    assert candidate_3_climate_data['station_name'] == 'tester_3'
    assert candidate_3_climate_data['lat'] == 0
    assert candidate_3_climate_data['lng'] == 0
    assert candidate_3_climate_data['area_km2'] == 1
    assert candidate_3_climate_data['min_elev'] == 0
    assert candidate_3_climate_data['avg_elev'] == 1
    assert candidate_3_climate_data['max_elev'] == 2
    assert candidate_3_climate_data['month'] == [4, 9, 6, 8, 3, 7, 11, 2, 10, 1, 5, 12]
    assert candidate_3_climate_data['ppt'] == [1] * 12
    assert candidate_3_climate_data['pas'] == [1] * 12
    assert candidate_3_climate_data['tave'] == [1] * 12

def test_generate_hydrologic_variability():
    """
        Simple reformatting funciton
    """
    # Empty input/output case
    hv_raw = []

    result = generate_hydrologic_variability(hv_raw)

    assert result == {
        "Candidate1": {
            "candidates": {},
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}
        },
        "Candidate2": {
            "candidates": {},
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}

        },
        "Candidate3": {
            "candidates": {},
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}
        }
    }

    # Single month of data
    hv_raw = [
        {
            'month': 1,
            'month_value': {
                'c1': 1,
                'q_m3s_c1': [1,2,3,4,5],
                'c2': 2,
                'q_m3s_c2': [5,6,7,8,9],
                'c3': 3,
                'q_m3s_c3': [10,11,12,13,14]
            }
        }
    ]

    result = generate_hydrologic_variability(hv_raw)

    candidate_1 = result['Candidate1']
    assert candidate_1['candidates'] == {1:1}
    assert candidate_1['90th'] == {1:5}
    assert candidate_1['75th'] == {1:4}
    assert candidate_1['50th'] == {1:3}
    assert candidate_1['25th'] == {1:2}
    assert candidate_1['10th'] == {1:1}

    candidate_2 = result['Candidate2']
    assert candidate_2['candidates'] == {1:2}
    assert candidate_2['90th'] == {1:9}
    assert candidate_2['75th'] == {1:8}
    assert candidate_2['50th'] == {1:7}
    assert candidate_2['25th'] == {1:6}
    assert candidate_2['10th'] == {1:5}

    candidate_3 = result['Candidate3']
    assert candidate_3['candidates'] == {1:3}
    assert candidate_3['90th'] == {1:14}
    assert candidate_3['75th'] == {1:13}
    assert candidate_3['50th'] == {1:12}
    assert candidate_3['25th'] == {1:11}
    assert candidate_3['10th'] == {1:10}

    # Full year of data
    hv_raw = [
        {
            'month': i,
            'month_value': {
                'c1': 1,
                'q_m3s_c1': [1+i,2+i,3+i,4+i,5+i],
                'c2': 2,
                'q_m3s_c2': [5+i,6+i,7+i,8+i,9+i],
                'c3': 3,
                'q_m3s_c3': [10+i,11+i,12+i,13+i,14+i]
            }
        }
        for i in range(1,13)
    ]

    result = generate_hydrologic_variability(hv_raw)

    candidate_1 = result['Candidate1']
    assert candidate_1['candidates'] == {i:1 for i in range(1,13)}
    assert candidate_1['90th'] == {i:5+i for i in range(1,13)}
    assert candidate_1['75th'] == {i:4+i for i in range(1,13)}
    assert candidate_1['50th'] == {i:3+i for i in range(1,13)}
    assert candidate_1['25th'] == {i:2+i for i in range(1,13)}
    assert candidate_1['10th'] == {i:1+i for i in range(1,13)}

    candidate_2 = result['Candidate2']
    assert candidate_2['candidates'] == {i:2 for i in range(1,13)}
    assert candidate_2['90th'] == {i:9 + i for i in range(1,13)}
    assert candidate_2['75th'] == {i:8 + i for i in range(1,13)}
    assert candidate_2['50th'] == {i:7 + i for i in range(1,13)}
    assert candidate_2['25th'] == {i:6 + i for i in range(1,13)}
    assert candidate_2['10th'] == {i:5 + i for i in range(1,13)}

    candidate_3 = result['Candidate3']
    assert candidate_3['candidates'] == {i:3 for i in range(1,13)}
    assert candidate_3['90th'] == {i:14 + i for i in range(1,13)}
    assert candidate_3['75th'] == {i:13 + i for i in range(1,13)}
    assert candidate_3['50th'] == {i:12 + i for i in range(1,13)}
    assert candidate_3['25th'] == {i:11 + i for i in range(1,13)}
    assert candidate_3['10th'] == {i:10 + i for i in range(1,13)}

def test_generate_future_hydrologic_variability():
    """
        Formatting function once again
    """
    # Empty test first
    future_hydrologic_variability_data = {}

    result = generate_future_hydrologic_variability(future_hydrologic_variability_data)

    assert result == {
        "1976": {
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}
        },
        "2011": {
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}

        },
        "2041": {
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}
        },
        "2071": {
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}
        }
    }

    # Simple test, small number of inputs (one data point for one month)
    future_hydrologic_variability_data = {
        'nc_p10_m01_06': 1,
        'nc_p10_m01_20': 2,
        'nc_p10_m01_50': 3,
        'nc_p10_m01_80': 4
    }

    result = generate_future_hydrologic_variability(future_hydrologic_variability_data)

    index = 1
    for year in result.keys():
        assert result[year]["10th"] == {1: index}
        assert result[year]["25th"] == {}
        assert result[year]["50th"] == {}
        assert result[year]["75th"] == {}
        assert result[year]["90th"] == {}
        index += 1

    # Simple test, p10 for a whole year
    future_hydrologic_variability_data = {f'nc_p10_m{i:02}_06': 1+i for i in range(1,13)}
    future_hydrologic_variability_data.update({f'nc_p10_m{i:02}_20': 2+i for i in range(1,13)})
    future_hydrologic_variability_data.update({f'nc_p10_m{i:02}_50': 3+i for i in range(1,13)})
    future_hydrologic_variability_data.update({f'nc_p10_m{i:02}_80': 4+i for i in range(1,13)})

    result = generate_future_hydrologic_variability(future_hydrologic_variability_data)

    index = 1
    for year in result.keys():
        assert result[year]["10th"] == {i: index + i for i in range(1,13)}
        assert result[year]["25th"] == {}
        assert result[year]["50th"] == {}
        assert result[year]["75th"] == {}
        assert result[year]["90th"] == {}
        index += 1

    # Full test for all percentages
    percentages = ['10', '25', '50', '75', '90']
    index = 0
    for percentage in percentages:
        future_hydrologic_variability_data.update({f'nc_p{percentage}_m{i:02}_06': 1+i+index for i in range(1,13)})
        future_hydrologic_variability_data.update({f'nc_p{percentage}_m{i:02}_20': 2+i+index for i in range(1,13)})
        future_hydrologic_variability_data.update({f'nc_p{percentage}_m{i:02}_50': 3+i+index for i in range(1,13)})
        future_hydrologic_variability_data.update({f'nc_p{percentage}_m{i:02}_80': 4+i+index for i in range(1,13)})
        index += 1

    result = generate_future_hydrologic_variability(future_hydrologic_variability_data)

    index = 1
    for year in result.keys():
        assert result[year]["10th"] == {i: index + i for i in range(1,13)}
        assert result[year]["25th"] == {i: index + i + 1 for i in range(1,13)}
        assert result[year]["50th"] == {i: index + i + 2 for i in range(1,13)}
        assert result[year]["75th"] == {i: index + i + 3 for i in range(1,13)}
        assert result[year]["90th"] == {i: index + i + 4 for i in range(1,13)}

        index += 1

def test_post_process_bus_stops():

    bus_stops = [
        {"fwa_watershed_code": "123-000000-000000", "name": "First River"},
        {"fwa_watershed_code": WILLISTON_FWA, "name": "Second River"},
        {"fwa_watershed_code": "123-000000-000000", "name": "Third River"},
    ]
    result = post_process_bus_stops(bus_stops)
    assert result[1] == "Williston Lake"
    assert result[2] == "Second River"

    bus_stops = [{"fwa_watershed_code": "100-000000-000000", "name": "Mackenzie River"}]
    result = post_process_bus_stops(bus_stops)
    assert result[-1] == "Arctic Ocean"

    bus_stops = [{"fwa_watershed_code": "200-000000-000000", "name": "Yukon River"}]
    result = post_process_bus_stops(bus_stops)
    assert result[-1] == "Bering Sea"

    bus_stops = [{"fwa_watershed_code": "300-000000-000000", "name": "Fraser River"}]
    result = post_process_bus_stops(bus_stops)
    assert result[-1] == "Pacific Ocean"

    bus_stops = [{"fwa_watershed_code": "100-123456-123456-654321-000000", "name": "First Named River"}] + [
        {"fwa_watershed_code": "100-123456-123456-000000-000000", "name": "Unnamed Basin"} for _ in range(5)] + [
        {"fwa_watershed_code": "100-123456-123456-654322-000000", "name": "Second Named River"}] + [
        {"fwa_watershed_code": "100-123456-123456-000000-000000", "name": "Unnamed Basin"} for _ in range(8)]

    result = post_process_bus_stops(bus_stops)
    # length of the input list will be 16 after the pacific ocean is added so lets confirm that the first 5 Unnamed Basin entries are removed leaving Second Named River as the second entry
    assert len(result) == 10
    assert result[0] == "First Named River"
    assert result[1] == "Second Named River"
    assert result[2:9] == ["Unnamed Basin"] * 7
    assert result[-1] == "Pacific Ocean"

    bus_stops = [{"fwa_watershed_code": "100-123456-123456-000000-000000", "name": f"River {i}"} for i in range(15)]
    result = post_process_bus_stops(bus_stops)
    assert len(result) == 10
    assert result[0] == "River 0"
    assert result[1] == "River 7"
    assert result[-2] == "River 14"

    with pytest.raises(ValueError):
        post_process_bus_stops([])


def test_build_fwa_list():
    fwa_code = "100-123456-789000-000000-000000-000000-000000-000000"
    result = build_fwa_list(fwa_code)
    assert result[0] == "100-000000-000000-000000-000000-000000-000000-000000"
    assert result[1] == "100-123456-000000-000000-000000-000000-000000-000000"
    assert result[2] == "100-123456-789000-000000-000000-000000-000000-000000"
    assert len(result) == 3

    fwa_code = "000000-000000-000000"
    result = build_fwa_list(fwa_code)
    assert result == []

    fwa_code = "123-000000-000000-000000"
    result = build_fwa_list(fwa_code)
    assert result == ["123-000000-000000-000000"]

    fwa_code = "123"
    result = build_fwa_list(fwa_code)
    assert result == ["123"]

    fwa_code = ""
    result = build_fwa_list(fwa_code)
    assert result == [""]
