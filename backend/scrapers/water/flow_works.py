from utils.etlpipeline_child_classes import StationObservationPipeline

class FlowWorksPipeline(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="FlowWorks CRD", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __implementation_specific_private_func(self):
        pass
