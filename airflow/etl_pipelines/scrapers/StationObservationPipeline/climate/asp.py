from scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline

class AspPipeline(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="ASP", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below
        self.station_source = 'temp'

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __implementation_specific_private_func(self):
        pass
