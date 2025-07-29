from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline

"""
The class below is used to test DataBcPipeline class' concrete methods which are:
    - download_data()
So any abstract method will be defined to return None
"""
class TestDataBcPipeline(DataBcPipeline):
    __test__ = False

    def __init__(self):
        super().__init__(name="test", url="test", destination_tables=["test"], databc_layer_name="test")

    def download_data(self):
        return None
