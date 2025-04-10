from utils.eltpipeline_class import EtlPipeline

class StationObservationPipeline(EtlPipeline):
    def __init__(self, name, url, destination_tables, station_url_format):
        # Initializing attributes in parent
        super().__init__(name=name, source_url=url, destination_tables=destination_tables)

        # Initializing attributes in child
        self.station_list = None
        self.station_url_format = station_url_format
        pass

    def download_data(self):
        pass

    def get_gauge_list(self):
        pass

class DataBcPipeline(EtlPipeline):
    def __init__(self, name, url, destination_tables, databc_layer_name):
        # Initializing attributes in parent
        super().__init__(name=name, source_url=url, destination_tables=destination_tables)

        # Initializing attributes in child
        self.databc_layer_name = databc_layer_name
        # Private attribute
        self.__downloaded_data = None

    def download_data(self):
        pass
