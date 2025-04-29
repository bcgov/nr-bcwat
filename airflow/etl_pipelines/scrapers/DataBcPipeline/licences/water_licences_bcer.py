from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline

class WaterLicencesBCERPipeline(DataBcPipeline):
    def __init__(self):
        super().__init__(name="Water Licences BCER", url="https://data-bc-er.opendata.arcgis.com//datasets/fcc52c0cfb3e4bffb20518880ec36fd0_0.geojson", destination_tables=["temp"], databc_layer_name=None)
        
        # Add other attributes as needed

    
    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def __some_private_function(self):
        pass
