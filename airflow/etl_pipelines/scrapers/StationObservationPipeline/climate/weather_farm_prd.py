from scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline

class WeatherFarmPrdPipeline(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="Weather Farm PRD", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below
        self.station_source = 'temp'

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __implementation_specific_private_func(self):
        pass
