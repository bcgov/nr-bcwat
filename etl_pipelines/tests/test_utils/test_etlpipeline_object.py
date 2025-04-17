from scrapers.EtlPipeline import EtlPipeline
from scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline

"""
The class below is used to test the EtlPipeline class' concrete methods which are:
    - load_data()
    - __load_data_into_tables()
    - get_downloaded_data()
    - get_transformed_data()
So any abstract method will be defined to return None.
"""
class TestEtlPipeline(EtlPipeline):
    __test__ = False

    def __init__(self, name, source_url, destination_tables):
        super().__init__(name, source_url, destination_tables)

    def download_data(self):
        return None 
    
    def validate_downloaded_data(self):
        return None
    
    def transform_data(self):
        return None

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
