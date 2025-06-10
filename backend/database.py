class Database:
    def get_climate_station_report_by_id(self, **args):
        from queries.climate.get_climate_station_report_by_id import get_climate_station_report_by_id_query

        return get_climate_station_report_by_id_query

    def get_climate_stations(self, **args):
        from queries.climate.get_climate_stations import get_climate_stations_query

        return get_climate_stations_query

    def get_groundwater_level_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_level_station_report_by_id import get_groundwater_level_station_report_by_id_query

        return get_groundwater_level_station_report_by_id_query

    def get_groundwater_level_stations(self, **args):
        from queries.groundwater.get_groundwater_level_stations import get_groundwater_level_stations_query

        return get_groundwater_level_stations_query

    def get_groundwater_quality_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_quality_station_report_by_id import get_groundwater_quality_station_report_by_id_query

        return get_groundwater_quality_station_report_by_id_query

    def get_groundwater_quality_stations(self, **args):
        from queries.groundwater.get_groundwater_quality_stations import get_groundwater_quality_stations_query

        return get_groundwater_quality_stations_query

    def get_streamflow_station_report_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_report_by_id import get_streamflow_station_report_by_id_query

        return get_streamflow_station_report_by_id_query

    def get_streamflow_stations(self, **args):
        from queries.streamflow.get_streamflow_stations import get_streamflow_stations_query

        return get_streamflow_stations_query

    def get_surface_water_station_report_by_id(self, **args):
        from queries.surface_water.get_surface_water_station_report_by_id import get_surface_water_station_report_by_id_query

        return get_surface_water_station_report_by_id_query

    def get_streamflow_station_report_flow_duration_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_report_flow_duration_by_id import get_streamflow_station_report_flow_duration_by_id_query

        return get_streamflow_station_report_flow_duration_by_id_query

    def get_surface_water_stations(self, **args):
        from queries.surface_water.get_surface_water_stations import get_surface_water_stations_query

        return get_surface_water_stations_query

    def get_watershed_station_report_by_id(self, **args):
        from queries.watershed.get_watershed_station_report_by_id import get_watershed_station_report_by_id_query

        return get_watershed_station_report_by_id_query

    def get_watershed_stations(self, **args):
        from queries.watershed.get_watershed_stations import get_watershed_stations_query

        return get_watershed_stations_query




