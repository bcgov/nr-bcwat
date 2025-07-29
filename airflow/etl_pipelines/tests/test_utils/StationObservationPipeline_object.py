from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline

"""
The class below is used to test StationObservationPipeline class' concrete methods which are:
    - download_data()
    - get_gauge_list()
So any abstract method will be defined to return None
"""
class TestStationObservationPipeline(StationObservationPipeline):
    __test__ = False

    def __init__(self):
        super().__init__(name="test", url="test", destination_tables=["test"])

    def transform_data(self):
        return None

    def validate_downloaded_data(self):
        return None
