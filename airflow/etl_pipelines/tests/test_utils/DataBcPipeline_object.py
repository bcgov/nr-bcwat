from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline

"""
The class below is used to test DataBcPipeline class' concrete methods.
So any abstract method will be defined to return None
"""
class TestDataBcPipeline(DataBcPipeline):
    __test__ = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def transform_data(self):
        return None
