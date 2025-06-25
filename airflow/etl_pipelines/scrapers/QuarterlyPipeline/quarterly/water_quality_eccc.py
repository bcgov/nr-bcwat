from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_ECCC_DTYPE_SCHEMA,
    QUARTERLY_ECCC_BASE_URLS,
    QUARTERLY_ECCC_DESTINATION_TABLES,
    QUARTERLY_ECCC_NAME,
    QUARTERLY_ECCC_RENAME_DICT,
    QUARTERLY_ECCC_STATION_NETWORK_ID,
    QUARTERLY_ECCC_STATION_SOURCE,
    MAX_NUM_RETRY
)
from etl_pipelines.utils.functions import setup_logging
from urllib.request import urlopen
from time import sleep
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

    def download_data(self):
        logger.info(f"Downloading data for {self.name}")

        for key in self.source_url.keys():
            logger.debug(f"Downloading data from URL: {self.source_url[key]}")
            self._EtlPipeline__download_num_retries = 0
            failed = False

            while True:
                try:
                    response = urlopen(self.source_url[key])
                except Exception as e:
                    if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                        logger.warning(f"Error downloading data from URL: {self.source_url[key]}. Retrying...")
                        self._EtlPipeline__download_num_retries += 1
                        sleep(5)
                        continue
                    else:
                        logger.error(f"Error downloading data from URL: {self.source_url[key]}. Raising Error {e}", exc_info=True)
                        failed = True
                        break

                if response.status != 200:
                    if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                        logger.warning(f"Response status was not 200. Retrying...")
                        self._EtlPipeline__download_num_retries += 1
                        sleep(5)
                        continue
                    else:
                        logger.error(f"Response status was not 200. Raising Error {e}", exc_info=True)
                        failed = True
                        break

                break

            if failed:
                logger.error(f"Failed to download data from URL: {self.source_url[key]}. Please check for the errors and make fixes. Raising Error.")
                raise RuntimeError(f"Failed to download data from URL: {self.source_url[key]}. This was unexpected. Please Debug")

            try:
                logger.debug(f"Loading data into LazyFrame")
                lf = pl.scan_csv(response.read(), eol_char="\r\n", schema_overrides=self.expected_dtype[key], null_values=["NV", "Null", "NA"])
            except Exception as e:
                logger.error(f"Error when loading data in to LazyFrame, error: {e}")
                raise RuntimeError(f"Error when loading data in to LazyFrame, error: {e}")

            # Check if the data is empty
            if lf.limit(1).collect().is_empty():
                logger.error(f"Downloaded data is empty for URL: {self.source_url[key]}. This was not expected. Please check for the reason it is empty. Raising Error.")
                raise RuntimeError(f"Downloaded data is empty for URL: {self.source_url[key]}. This was not expected. Please check for the reason it is empty.")

            self._EtlPipeline__downloaded_data[key] = lf

        logger.info(f"Finished downloading data for {self.name}")

    def transform_data(self):
        logger.info(f"Starting transformation for {self.name}")
        downloaded_data = self.get_downloaded_data()

        for key in downloaded_data.keys():
            logger.debug(f"Transforming data for key: {key}")

            data = {
                downloaded_data[key]
                .
            }

        logger.info(f"Finished transforming for {self.name}")

    def validate_downloaded_data(self):
        pass

    def get_and_insert_new_stations(self, station_data=None):
        pass
