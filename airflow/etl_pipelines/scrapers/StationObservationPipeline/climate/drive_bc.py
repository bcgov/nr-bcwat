from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    DRIVE_BC_DESTINATION_TABLES,
    DRIVE_BC_BASE_URL,
    DRIVE_BC_DTYPE_SCHEMA,
    DRIVE_BC_NAME,
    DRIVE_BC_NETWORK_ID,
    DRIVE_BC_RENAME_DICT,
    DRIVE_BC_STATION_SOURCE,
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class DriveBcPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=DRIVE_BC_NAME, 
            source_url=DRIVE_BC_BASE_URL, 
            destination_tables=DRIVE_BC_DESTINATION_TABLES,
            days=2,
            station_source=DRIVE_BC_STATION_SOURCE,
            expected_dtype=DRIVE_BC_DTYPE_SCHEMA,
            column_rename_dict=DRIVE_BC_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=False,
            network_ids= DRIVE_BC_NETWORK_ID,
            db_conn=db_conn
            )

        

    def transform_data(self):
        logger.info(f"Transforming downloaded data for {self.name}")

        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
        
        # TODO: Check for new stations, and insert them into the database if they are new, along with their metadata. Send Email after completion.

        logger.debug(f"Starting Transformation")

        df = downloaded_data["drive_bc"]

        try:
            # Unfortunately all the value columns of the data have their units attached to it. So we will have to remove them here
            df = (
                df
                .rename(self.column_rename_dict)
                .drop("received", "elevation", "event", "dataStatus")
                .with_columns(
                    airTemp = pl.col("airTemp")
                )

            )
        except Exception as e:
            logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")

    def get_and_insert_new_stations(self, station_data=None):
        pass

