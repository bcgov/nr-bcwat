from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_ECCC_DTYPE_SCHEMA,
    QUARTERLY_ECCC_BASE_URLS,
    QUARTERLY_ECCC_DESTINATION_TABLES,
    QUARTERLY_ECCC_NAME,
    QUARTERLY_ECCC_RENAME_DICT,
    QUARTERLY_ECCC_STATION_NETWORK_ID,
    QUARTERLY_ECCC_STATION_SOURCE,
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class QuarterlyWaterQualityEcccPipeline(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="Quarterly Water Quality ECCC", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below
        self.station_source = 'temp'

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def __implementation_specific_private_func(self):
        pass
