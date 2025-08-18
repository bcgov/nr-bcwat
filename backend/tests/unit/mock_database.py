import os
import json
from test_utils import load_fixture

class MockDatabase:

    def get_stations_by_type(self, **args):
        match args['type_id']:
            case [2]:
                from fixtures.groundwater.groundwater_level_stations import groundwater_level_stations
                return groundwater_level_stations
                # return load_fixture("groundwater", "groundwaterLevelStationsQuery.json")
            case [4]:
                from fixtures.surface_water.surface_water_stations import surface_water_stations
                return surface_water_stations
            case [5]:
                from fixtures.groundwater.groundwater_quality_stations import groundwater_quality_stations
                return groundwater_quality_stations

    def get_station_by_type_and_id(self, **args):
        match args['type_id']:
            case [1]:
                match args['station_id']:
                    case 1:
                        return None
                    case 42373:
                        return {
                            "name": "Bitter Creek at Glacier Hwy (37A) Bridge",
                            "nid": "08DC0002",
                            "net": 53,
                            "yr": [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
                            "ty" : "Hydrometric Surface Water",
                            "description": None,
                            "licence_link": "unit-test-link/unit-test-license"
                        }
                    case 47214:
                        return {
                            'id': 47214,
                            'name': 'Forrest Kerr Creek Above 460 M Contour',
                            'net': 1,
                            'nid': '08CG006',
                            'latitude': 56.91556167602539,
                            'longitude': -130.7208251953125,
                            'description': None,
                            'ty': 'Hydrometric Surface Water',
                            'area': 311.0,
                            'licence_link': 'unit-test-link/unit-test-license',
                            'yr': [1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994]
                        }
                    case 42648:
                        return {
                            'id': 42648,
                            'name': 'Omineca River Above Osilinka River',
                            'net': 1,
                            'nid': '07EC002',
                            'latitude': 55.9168586730957,
                            'longitude': -124.56758117675781,
                            'description': None,
                            'ty': 'Hydrometric Surface Water',
                            'area': 5560.0,
                            'licence_link': 'unit-test-link/unit-test-license',
                            'yr': [1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
                        }
            case [2]:
                match args['station_id']:
                    case 1:
                        return None
                    case 2:
                        return {
                            "name" : "unit_test",
                            "nid" : -1,
                            "net" : "unit test nw",
                            "yr": [2000, 2001],
                            "ty" : "tyty",
                            "description" : None,
                            "licence_link" : "test.com"
                        }
                    case 16425:
                        from fixtures.groundwater.station_16425_metadata import station_metadata
                        return station_metadata
            case [3, 6]:
                match args['station_id']:
                    case 1:
                        # Precip/Temperature
                        from fixtures.climate.station_1_metadata import climate_station_1_metadata
                        return climate_station_1_metadata
                    case 287:
                        # SWE/SnowDepth
                        from fixtures.climate.station_287_metadata import climate_station_287_metadata
                        return climate_station_287_metadata
                    case 17401:
                        # Manual Snow Survey
                        from fixtures.climate.station_17401_metadata import climate_station_17401_metadata
                        return climate_station_17401_metadata
                    case 47421:
                        # Empty Data Case
                        from fixtures.climate.station_47421_metadata import climate_station_47421_metadata
                        return climate_station_47421_metadata
                    case 47538:
                        # Improperly Formatted Data Case
                        from fixtures.climate.station_47538_metadata import climate_station_47538_metadata
                        return climate_station_47538_metadata
            case [4]:
                match args['station_id']:
                    case 41773:
                        from fixtures.surface_water.station_41773_metadata import station_metadata
                        return station_metadata
            case [5]:
                match args['station_id']:
                    case 1:
                        return None
                    case 2:
                        return {
                            "name" : "unit_test",
                            "nid" : -1,
                            "net" : "unit test nw",
                            "yr": [2000, 2001],
                            "ty" : "tyty",
                            "description" : None,
                            "licence_link" : "test.com"
                        }
                    case 15045:
                        from fixtures.groundwater.station_16425_metadata import station_metadata
                        return station_metadata

        return None

    def get_climate_station_report_by_id(self, **args):
        match args['station_id']:
            case 1:
                # Precip/Temperature
                from fixtures.climate.station_1_metrics import climate_station_1_metrics
                return climate_station_1_metrics
            case 287:
                # SWE/SnowDepth
                from fixtures.climate.station_287_metrics import climate_station_287_metrics
                return climate_station_287_metrics
            case 17401:
                # Manual Snow Survey
                from fixtures.climate.station_17401_metrics import climate_station_17401_metrics
                return climate_station_17401_metrics
            case 47538:
                # Improperly Formatted Data Case
                from fixtures.climate.station_47538_metrics import climate_station_47538_metrics
                return climate_station_47538_metrics
        return []

    def get_groundwater_level_station_report_by_id(self, **args):
        match args['station_id']:
            case 2:
                return []
            case 16425:
                from fixtures.groundwater.station_16425_metrics import station_metrics
                return station_metrics

    def get_groundwater_quality_station_report_by_id(self, **args):
        match args['station_id']:
            case 2:
                return []
            case 15045:
                from fixtures.groundwater.station_15045_metrics import station_metrics
                return station_metrics

    def get_streamflow_station_report_by_id(self, **args):
        match args['station_id']:
            case 42373:
                from fixtures.streamflow.station_42373_metrics import station_metrics
                return station_metrics
            case 47214:
                from fixtures.streamflow.station_47214_metrics import station_metrics
                return station_metrics
            case 42648:
                from fixtures.streamflow.station_42648_metrics import station_metrics
                return station_metrics
            case 1:
                return []

    def get_streamflow_station_flow_metrics_by_id(self, **args):
        match args['station_id']:
            case 42373:
                return None
            case 47214:
                from fixtures.streamflow.station_47214_flow_metrics import flow_metrics
                return flow_metrics
            case 42648:
                from fixtures.streamflow.station_42648_flow_metrics import flow_metrics
                return flow_metrics
        return None

    def get_surface_water_station_report_by_id(self, **args):
        match args['station_id']:
            case 41773:
                from fixtures.surface_water.station_41773_metrics import station_metrics
                return station_metrics

    def get_watershed_licences(self, **args):
        from fixtures.watershed.watershed_licenses import licenses
        return licenses

    def get_watershed_licences_by_search_term(self, **args):
        match args['licence_no']:
            case '404%':
                return []
            case '200%':
                return [1,2,3]

    def get_watershed_by_search_term(self, **args):
        match args['watershed_feature_id']:
            case 404:
                return []
            case 200:
                return [1,2,3]


    def get_watershed_by_id(self, **args):
        match args['watershed_feature_id']:
            case 404:
                return None
            case 200:
                return {
                    "wfi": 1,
                    "geojson": {"type" : "FeatureCollection"},
                    "name": "unit_test"
                }


    def get_watershed_stations(self, **args):
        path = os.path.join(os.path.dirname(__file__), 'fixtures/watershed/router', 'watershedStationsQuery.json')
        with open(path, 'r') as f:
            return json.load(f)

    def get_watershed_station_report_by_id(self, **args):
        return {}

    def get_water_quality_station_statistics(self, **args):
        return {
            'unique_params': 20,
            'sample_dates': 49
        }

    def get_climate_stations(self, **args):
        return load_fixture("climate", "getClimateStationsResponse.json")

    def get_streamflow_stations(self, **args):
        return load_fixture("streamflow", "router", "streamflowStationsResponse.json")

    def get_station_csv_metadata_by_type_and_id(self, **args):
        match args['type_id']:
            case [1]:
                match args['station_id']:
                    case 1:
                        return None
                    case 2:
                        return {'name' :"unit_test", "nid" : 1, "net" : "test_network", "description": "I am a unit test", "licence_link": "unit_test.com/unit"}
                    case 32509:
                        from fixtures.streamflow.station_32509_metrics import station_metrics
                        return station_metrics
            case [2]:
                match args['station_id']:
                    case 1:
                        return None
                    case 2:
                        return {'name' :"unit_test", "nid" : 1, "net" : "test_network", "description": "I am a unit test", "licence_link": "unit_test.com/unit"}
                    case 16425:
                        from fixtures.groundwater.station_16425_csv_metadata import csv_metadata
                        return csv_metadata
            case [4]:
                match args['station_id']:
                    case 1:
                        return None
                    case 2:
                        return {'name' :"unit_test", "nid" : 1, "net" : "test_network", "description": "I am a unit test", "licence_link": "unit_test.com/unit"}
                    case 41773:
                        from fixtures.surface_water.station_41773_csv_metadata import csv_metadata
                        return csv_metadata
            case [5]:
                match args['station_id']:
                    case 1:
                        return None
                    case 2:
                        return {'name' :"unit_test", "nid" : 1, "net" : "test_network", "description": "I am a unit test", "licence_link": "unit_test.com/unit"}
                    case 15045:
                        from fixtures.groundwater.station_15045_csv_metadata import csv_metadata
                        return csv_metadata
            case [3, 6]:
                match args['station_id']:
                    case 1:
                        return None
                    case 2:
                        return {'name' :"unit_test", "nid" : 1, "net" : "test_network", "description": "I am a unit test", "licence_link": "unit_test.com/unit"}
                    case 44432:
                        from fixtures.climate.station_44432_csv_metadata import csv_metadata
                        return csv_metadata
                    case 32555:
                        from fixtures.climate.station_32555_csv_metadata import csv_metadata
                        return csv_metadata

        return None

    def get_streamflow_station_csv_by_id(self, **args):
        match args['station_id']:
            case 2:
                return []
            case 32509:
                from fixtures.streamflow.station_32509_csv import csv_metrics
                return csv_metrics

    def get_water_quality_station_csv_by_id(self, **args):
        match args['station_id']:
            case 2:
                return []
            case 41773:
                from fixtures.surface_water.station_41773_csv_metrics import station_metrics
                return station_metrics
            case 15045:
                from fixtures.groundwater.station_15045_csv_data import csv_data
                return csv_data

    def get_groundwater_level_station_csv_by_id(self, **args):
        match args['station_id']:
            case 2:
                return []
            case 16425:
                from fixtures.groundwater.station_16425_csv_data import csv_data
                return csv_data

    def get_climate_station_csv_by_id(self, **args):
        match args['station_id']:
            case 2:
                return []
            case 44432:
                from fixtures.climate.station_44432_csv_data import csv_data
                return csv_data
            case 32555:
                from fixtures.climate.station_32555_csv_data import csv_data
                return csv_data

    def get_watershed_region_by_id(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                return {"region_id": 4}
            case 9191927:
                return {"region_id": 3}
            case 10255303:
                return {"region_id": 6}
            case 9196070:
                return {"region_id": 5}


    def get_watershed_report_by_id(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                from fixtures.watershed.wfi_9253853_watershed_metadata import watershed_metadata
                return watershed_metadata
            case 9191927:
                from fixtures.watershed.wfi_9191927_watershed_metadata import watershed_metadata
                return watershed_metadata
            case 10255303:
                from fixtures.watershed.wfi_10255303_watershed_metadata import watershed_metadata
                return watershed_metadata
            case 9196070:
                from fixtures.watershed.wfi_9196070_watershed_metadata import watershed_metadata
                return watershed_metadata

    def get_watershed_fwa_by_id(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                from fixtures.watershed.wfi_9253853_fwa_id import fwa_id
                return fwa_id
            case 9191927:
                from fixtures.watershed.wfi_9191927_fwa_id import fwa_id
                return fwa_id
            case 10255303:
                from fixtures.watershed.wfi_10255303_fwa_id import fwa_id
                return fwa_id
            case 9196070:
                from fixtures.watershed.wfi_9196070_fwa_id import fwa_id
                return fwa_id

    def get_watershed_bus_stops_by_ids(self, **args):
        from fixtures.watershed.wfi_9253853_fwa_id import fwa_id as fwa_id_9253853
        from fixtures.watershed.wfi_9191927_fwa_id import fwa_id as fwa_id_9191927
        from fixtures.watershed.wfi_10255303_fwa_id import fwa_id as fwa_id_10255303
        from fixtures.watershed.wfi_9196070_fwa_id import fwa_id as fwa_id_9196070

        watershed_id = args['fwa_watershed_codes'][-1]

        if watershed_id == fwa_id_9253853['fwa_watershed_code']:
            from fixtures.watershed.wfi_9253853_bus_stops import bus_stops
            return bus_stops
        elif watershed_id == fwa_id_9191927['fwa_watershed_code']:
            from fixtures.watershed.wfi_9191927_bus_stops import bus_stops
            return bus_stops
        elif watershed_id == fwa_id_10255303['fwa_watershed_code']:
            from fixtures.watershed.wfi_10255303_bus_stops import bus_stops
            return bus_stops
        elif watershed_id == fwa_id_9196070['fwa_watershed_code']:
            from fixtures.watershed.wfi_9196070_bus_stops import bus_stops
            return bus_stops


    def get_kwt_hydrologic_variability_by_id(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                from fixtures.watershed.watershed_9253853_future_hydrologic_variability import future_hydrologic_variability
                return future_hydrologic_variability

    def get_watershed_allocations_by_id(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                from fixtures.watershed.watershed_9253853_watershed_allocations import watershed_allocations
                return watershed_allocations
            case 9191927:
                from fixtures.watershed.watershed_9191927_watershed_allocations import watershed_allocations
                return watershed_allocations
            case 10255303:
                from fixtures.watershed.watershed_9191927_watershed_allocations import watershed_allocations
                return watershed_allocations
            case 9196070:
                from fixtures.watershed.watershed_9196070_watershed_allocations import watershed_allocations
                return watershed_allocations

    def get_watershed_industry_allocations_by_id(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                from fixtures.watershed.watershed_9253853_industry_allocations import industry_allocations
                return industry_allocations
            case 9191927:
                from fixtures.watershed.watershed_9191927_industry_allocations import industry_allocations
                return industry_allocations
            case 10255303:
                from fixtures.watershed.watershed_10255303_industry_allocations import industry_allocations
                return industry_allocations
            case 9196070:
                from fixtures.watershed.watershed_9196070_industry_allocations import industry_allocations
                return industry_allocations

    def get_watershed_monthly_hydrology_by_id(self, **args):
        if(args['in_basin'] == 'query'):
            match args['watershed_feature_id']:
                case 9253853:
                    from fixtures.watershed.watershed_9253853_monthly_hydrology import monthly_hydrology
                    return monthly_hydrology
                case 9191927:
                    from fixtures.watershed.watershed_9191927_monthly_hydrology import monthly_hydrology
                    return monthly_hydrology
                case 10255303:
                    from fixtures.watershed.watershed_10255303_monthly_hydrology import monthly_hydrology
                    return monthly_hydrology
                case 9196070:
                    from fixtures.watershed.watershed_9196070_monthly_hydrology import monthly_hydrology
                    return monthly_hydrology
        elif(args['in_basin'] == 'downstream'):
            match args['watershed_feature_id']:
                case 9253853:
                    from fixtures.watershed.watershed_9253853_downstream_monthly_hydrology import downstream_monthly_hydrology
                    return downstream_monthly_hydrology
                case 9191927:
                    from fixtures.watershed.watershed_9191927_downstream_monthly_hydrology import downstream_monthly_hydrology
                    return downstream_monthly_hydrology
                case 10255303:
                    from fixtures.watershed.watershed_10255303_downstream_monthly_hydrology import downstream_monthly_hydrology
                    return downstream_monthly_hydrology
                case 9196070:
                    from fixtures.watershed.watershed_9196070_downstream_monthly_hydrology import downstream_monthly_hydrology
                    return downstream_monthly_hydrology

    def get_watershed_annual_hydrology_by_id(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                from fixtures.watershed.watershed_9253853_annual_hydrology import annual_hydrology
                return annual_hydrology
            case 9191927:
                from fixtures.watershed.watershed_9191927_annual_hydrology import annual_hydrology
                return annual_hydrology
            case 10255303:
                from fixtures.watershed.watershed_10255303_annual_hydrology import annual_hydrology
                return annual_hydrology
            case 9196070:
                from fixtures.watershed.watershed_9196070_annual_hydrology import annual_hydrology
                return annual_hydrology

    def get_licence_import_dates(self, **args):
        match args['watershed_feature_id']:
            case 9253853:
                from fixtures.watershed.watershed_9253853_licence_import_dates import licence_import_dates
                return licence_import_dates
            case 9191927:
                from fixtures.watershed.watershed_9191927_licence_import_dates import licence_import_dates
                return licence_import_dates
            case 10255303:
                from fixtures.watershed.watershed_10255303_licence_import_dates import licence_import_dates
                return licence_import_dates
            case 9196070:
                from fixtures.watershed.watershed_9196070_licence_import_dates import licence_import_dates
                return licence_import_dates


    def get_watershed_candidates_by_id(self, **args):
        match args['watershed_feature_id']:
            case 10255303:
                from fixtures.watershed.watershed_10255303_candidate_metadata import candidate_metadata
                return candidate_metadata
            case 9196070:
                from fixtures.watershed.watershed_9196070_candidate_metadata import candidate_metadata
                return candidate_metadata


    def get_watershed_hydrologic_variability_by_id(self, **args):
        match args['watershed_feature_id']:
            case 10255303:
                from fixtures.watershed.watershed_10255303_hydrologic_variability import hydrologic_variability
                return hydrologic_variability
            case 9196070:
                from fixtures.watershed.watershed_9196070_hydrologic_variability import hydrologic_variability
                return hydrologic_variability
