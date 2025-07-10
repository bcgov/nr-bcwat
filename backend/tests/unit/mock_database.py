import os
import json

class MockDatabase:

    def get_stations_by_type(self, **args):
        path = os.path.join(os.path.dirname(__file__), 'fixtures/streamflow', 'fullStreamflow.json')
        with open(path, 'r') as f:
            return json.load(f)

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

    def get_watershed_station_report_by_id(self, **args):
        return {}

    def get_watershed_stations(self, **args):
        return {}
