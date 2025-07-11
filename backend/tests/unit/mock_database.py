import os
import json

class MockDatabase:

    def get_stations_by_type(self, **args):
        match args['type_id']:
            case 1:
                path = os.path.join(os.path.dirname(__file__), 'fixtures/streamflow/router', 'streamflowStationsQuery.json')
            case 2:
                path = os.path.join(os.path.dirname(__file__), 'fixtures/groundwater/router', 'groundwaterLevelStationsQuery.json')
            case 3:
                path = os.path.join(os.path.dirname(__file__), 'fixtures/climate/router', 'climateStationsQuery.json')
            case 4:
                path = os.path.join(os.path.dirname(__file__), 'fixtures/surface_water/router', 'surfaceWaterStationsQuery.json')
            case 5:
                path = os.path.join(os.path.dirname(__file__), 'fixtures/groundwater/router', 'groundwaterQualityStationsQuery.json')

        with open(path, 'r') as f:
            return json.load(f)

    def get_station_by_type_and_id(self, **args):
        return{}

    def get_climate_station_report_by_id(self, **args):
        return {}

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
