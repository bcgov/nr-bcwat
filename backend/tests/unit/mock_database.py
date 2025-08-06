import os
import json
from test_utils import load_fixture

class MockDatabase:

    def get_stations_by_type(self, **args):
        match args['type_id']:
            case [2]:
                return load_fixture("groundwater", "groundwaterLevelStationsQuery.json")
            case [4]:
                return load_fixture("surface_water", "surfaceWaterStationsQuery.json")
            case [5]:
                return load_fixture("groundwater", "groundwaterQualityStationsQuery.json")

    def get_station_by_type_and_id(self, **args):
        match args['type_id']:
            case [1]:
                return
            case [2]:
                return
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
                return
            case [5]:
                return

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
        return {}

    def get_groundwater_quality_station_report_by_id(self, **args):
        return {}

    def get_streamflow_station_report_by_id(self, **args):
        return {}

    def get_streamflow_station_report_flow_duration_by_id(self, **args):
        return {}

    def get_surface_water_station_report_by_id(self, **args):
        return {}

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
