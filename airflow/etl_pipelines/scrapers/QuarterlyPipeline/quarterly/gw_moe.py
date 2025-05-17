from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline

class QuarterlyGwMoe(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="Quarterly GW MOE Archive", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below
        self.station_source = 'temp'

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def __implementation_specific_private_func(self):
        pass
