import os
import json
from test_utils import load_fixture

class MockDatabase:

    def get_stations_by_type(self, **args):
        match args['type_id']:
            case [1]:
                return load_fixture("streamflow", "router", "streamflowStationsQuery.json")
            case [2]:
                return load_fixture("groundwater", "router", "groundwaterLevelStationsQuery.json")
            case [3, 6]:
                return load_fixture("climate", "router", "climateStationsQuery.json")
            case [4]:
                return load_fixture("surface_water", "router", "surfaceWaterStationsQuery.json")
            case [5]:
                return load_fixture("groundwater", "router", "groundwaterQualityStationsQuery.json")

    def get_station_by_type_and_id(self, **args):
        match args['type_id']:
            case [1]:
                return
            case [2]:
                return
            case [3, 6]:
                match args['station_id']:
                    case 1:
                        from fixtures.climate.router.station_1_metadata import climate_station_metadata
                        return climate_station_metadata
                    case 47421:
                        from fixtures.climate.router.station_47421_metadata import climate_station_metadata
                        return climate_station_metadata
                    case 47538:
                        from fixtures.climate.router.station_47538_metadata import climate_station_metadata
                        return climate_station_metadata
            case [4]:
                return
            case [5]:
                return

        return None

    def get_climate_station_report_by_id(self, **args):
        match args['station_id']:
            case 1:
                from fixtures.climate.router.station_1_metrics import climate_station_metrics
                return climate_station_metrics
            case 47538:
                from fixtures.climate.router.station_47538_metrics import improper_climate_station_metrics
                return improper_climate_station_metrics
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
