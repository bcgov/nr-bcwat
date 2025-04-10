from abc import ABC, abstractmethod

class EtlPipeline(ABC):

    def __init__(self, name, source_url, destination_tables):
        # Public Attributes
        self.name = name
        self.source_url = source_url
        self.destination_tables = destination_tables
        
        #Private Attributes
        self.__download_num_retries = 0
        self.__downloaded_data = None
        self.__transformed_data = None

    @abstractmethod
    def download_data(self):
        """Download data files from URLs"""
        pass

    @abstractmethod
    def validate_downloaded_data(self):
        """Check that the downloaded data is valid and shaped correctly"""
        pass

    @abstractmethod
    def transform_data(self):
        """Apply the required transformation for the data that was downloaded"""
        pass

    def load_data(self):
        pass

    def __load_data_into_tables(self):
        pass

    def get_downloaded_data(self):
        pass

    def get_transformed_data(self):
        pass

