from utils.etlpipeline_child_classes import DataBcPipeline

class WaterApprovalPointsPipeline(DataBcPipeline):
    def __init__(self):
        super().__init__(name="Water Approval Points DataBC", url="tempurl", destination_tables=["temp"], databc_layer_name="water-approval-points")
        
        # Add other attributes as needed

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __some_private_function(self):
        pass
