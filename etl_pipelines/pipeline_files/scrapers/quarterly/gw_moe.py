from etl_pipelines.pipeline_files.stationobservationpipeline_class import StationObservationPipeline

class QuarterlyGwMoe(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="Quarterly GW MOE Archive", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __implementation_specific_private_func(self):
        pass
