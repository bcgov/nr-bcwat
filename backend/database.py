class Database:
    def get_climate_reports(self, **args):
        from queries.climate.get_climate_reports import get_climate_reports_query

        return get_climate_reports_query

    def get_climate_stations(self, **args):
        from queries.climate.get_climate_stations import get_climate_stations_query

        return get_climate_stations_query

    def get_groundwater_level_reports(self, **args):
        from queries.groundwater.get_groundwater_level_reports import get_groundwater_level_reports_query

        return get_groundwater_level_reports_query

    def get_groundwater_level_stations(self, **args):
        from queries.groundwater.get_groundwater_level_stations import get_groundwater_level_stations_query

        return get_groundwater_level_stations_query

    def get_groundwater_quality_reports(self, **args):
        from queries.groundwater.get_groundwater_quality_reports import get_groundwater_quality_reports_query

        return get_groundwater_quality_reports_query

    def get_groundwater_quality_stations(self, **args):
        from queries.groundwater.get_groundwater_quality_stations import get_groundwater_quality_stations_query

        return get_groundwater_quality_stations_query

    def get_streamflow_reports(self, **args):
        from queries.streamflow.get_streamflow_reports import get_streamflow_reports_query

        return get_streamflow_reports_query

    def get_streamflow_stations(self, **args):
        from queries.streamflow.get_streamflow_stations import get_streamflow_stations_query

        return get_streamflow_stations_query

    def get_surface_water_reports(self, **args):
        from queries.surface_water.get_surface_water_reports import get_surface_water_reports_query

        return get_surface_water_reports_query

    def get_surface_water_stations(self, **args):
        from queries.surface_water.get_surface_water_stations import get_surface_water_stations_query

        return get_surface_water_stations_query

    def get_watershed_reports(self, **args):
        from queries.watershed.get_watershed_reports import get_watershed_reports_query

        return get_watershed_reports_query

    def get_watershed_stations(self, **args):
        from queries.watershed.get_watershed_stations import get_watershed_stations_query

        return get_watershed_stations_query




