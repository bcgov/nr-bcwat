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
import pendulum

logger = setup_logging()

class QuarterlyWaterQualityEcccPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=pendulum.now("UTC")):
        super().__init__(
            name=QUARTERLY_ECCC_NAME,
            source_url=QUARTERLY_ECCC_BASE_URLS,
            destination_tables=QUARTERLY_ECCC_DESTINATION_TABLES,
            days=2,
            station_source=QUARTERLY_ECCC_STATION_SOURCE,
            expected_dtype=QUARTERLY_ECCC_DTYPE_SCHEMA,
            column_rename_dict=QUARTERLY_ECCC_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype = True,
            network_ids=QUARTERLY_ECCC_STATION_NETWORK_ID,
            min_ratio={},
            db_conn=db_conn,
            date_now=date_now
        )


    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def __implementation_specific_private_func(self):
        pass
