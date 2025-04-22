from scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline

class WaterRightsApplicationsPublicPipeline(DataBcPipeline):
    def __init__(self):
        super().__init__(name="Water Rights Applications Public DataBC", url="tempurl", destination_tables=["temp"], databc_layer_name="water-rights-applications-public")
        
        # Add other attributes as needed

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __some_private_function(self):
        pass
