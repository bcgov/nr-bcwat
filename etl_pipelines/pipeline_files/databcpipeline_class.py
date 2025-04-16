from etl_pipelines.pipeline_files.eltpipeline_class import EtlPipeline
from utils.constants import logger

class DataBcPipeline(EtlPipeline):
    def __init__(self, name, url, destination_tables, databc_layer_name):
        # Initializing attributes in parent
        super().__init__(name=name, source_url=url, destination_tables=destination_tables)

        # Initializing attributes in child
        self.databc_layer_name = databc_layer_name
        # Private attribute
        self.__downloaded_data = None

    def download_data(self):
        logger.warning("download_data is not implemented yet, exiting")
        pass
