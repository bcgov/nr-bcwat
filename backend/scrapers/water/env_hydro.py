from utils.etlpipeline_child_classes import StationObservationPipeline

class EnvHydroPipeline(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="ENV Hydro Staging/Discharge", url='tempurl', destination_tables=["temp"], station_url_format="temp")

        ## Add Implementation Specific attributes below

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __implementation_specific_private_func(self):
        pass
