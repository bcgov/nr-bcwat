from utils.etlpipeline_child_classes import StationObservationPipeline

class EcXmlPipeline(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="EC XML", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __implementation_specific_private_func(self):
        pass
