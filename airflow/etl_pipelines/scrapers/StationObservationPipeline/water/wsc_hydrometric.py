from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    WSC_NAME,
    WSC_URL,
    WSC_DESTINATION_TABLES,
    WSC_STATION_SOURCE,
    WSC_DTYPE_SCHEMA,
    WSC_VALIDATE_COLUMNS,
    WSC_VALIDATE_DTYPES,
    WSC_RENAME_DICT
)
from etl_pipelines.utils.functions import setup_logging

from datetime import datetime, timedelta
import pytz
import polars as pl

logger = setup_logging()

class WscHydrometricPipeline(StationObservationPipeline):
    def __init__(self, db_conn = None, date_now = None):
        # Initializing attributes in parent class
        super().__init__(name=WSC_NAME, source_url=[], destination_tables=WSC_DESTINATION_TABLES)

        # Initializing attributes present class
        self.days = 2
        self.station_source = WSC_STATION_SOURCE
        self.station_list = None
        self.expected_dtype = WSC_DTYPE_SCHEMA
        self.validate_dtype = WSC_VALIDATE_DTYPES
        self.validate_column = WSC_VALIDATE_COLUMNS
        self.column_rename_dict = WSC_RENAME_DICT
        
        # Note that Once we use airflow this may have to change to a different way of getting the date especially if we want to use
        # it's backfill or catchup feature.
        self.db_conn = db_conn

        self.date_now = date_now.in_tz("America/Vancouver")
        self.source_url = {"wsc_daily_hydrometric.csv": WSC_URL.format(self.date_now.strftime("%Y%m%d"))}

        self.end_date = self.date_now.in_tz("UTC")
        self.start_date = self.end_date.subtract(days=self.days)

        self.get_station_list()
        

    def transform_data(self):
        """
        Implementation of the transform_data method for the class WscHydrometricPipeline. Since the downloaded data contains two different kinds of data that will be inserted into two separate tables of the database, common transformations have been made before splitting the data into two different dataframes. After which, the dataframes are transformed to match the schema of the database tables.

        Args: 
            None

        Output: 
            None
        """
        logger.debug(f"Starting Transformation step")
        # Get the downloaded data
        downloaded_data_list = self.get_downloaded_data()

        # Check if there is any downloaded data if not raise an error
        if not downloaded_data_list:
            logger.error("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")
            raise RuntimeError("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")

        # Transform the data
        try:
            colname_dict = self.column_rename_dict
            df = downloaded_data_list["wsc_daily_hydrometric.csv"]
        except KeyError as e:
            logger.error(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect.", exc_info=True)
            raise KeyError(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect. Error: {e}")
        
        # apply some transformations that will be done to both the dataframes:
        try:
            df = (
                df
                .rename(colname_dict)
                .select(colname_dict.values())
                .with_columns((pl.col("datestamp").str.to_datetime("%Y-%m-%dT%H:%M:%S%:z")).alias("datestamp"))
                .filter(pl.col("datestamp") > self.start_date)
                .with_columns(pl.col("datestamp").dt.convert_time_zone("America/Vancouver"))
                .with_columns(pl.col("datestamp").dt.date())
            )
        except pl.exceptions.ColumnNotFoundError as e:
            logger.error(f"Column could not be found or was not expected. Error: {e}", exc_info=True)
            raise pl.exceptions.ColumnNotFoundError(f"Column could not be found or was not expected. Error: {e}")

        # Apply transformations specific to the level values
        try:
            level_df = (
                df
                .select(pl.col("original_id"), pl.col("datestamp"), pl.col("level"))
                .rename({"level":"value"})
                .filter((pl.col("value").is_not_null()) & (pl.col("value") != 9999))
                .group_by(["original_id", "datestamp"]).mean()
                .with_columns(qa_id = 0, variable_id = 2)
                .join(self.station_list, on="original_id", how="inner")
                .drop(pl.col("original_id"))
                .select(pl.col("station_id"), pl.col("variable_id").cast(pl.Int8), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8))
            ).collect()
        except pl.exceptions.ColumnNotFoundError as e:
            logger.error(f"Column could not be found or was not expected when transforming level data. Error: {e}", exc_info=True)
            raise pl.exceptions.ColumnNotFoundError(f"Column could not be found or was not expected when transforming level data. Error: {e}")
        except TypeError as e:
            logger.error(f"TypeError occured, moste likely due to the fact that the station_list was not a LazyFrame. Error: {e}")
            raise TypeError(f"TypeError occured, moste likely due to the fact that the station_list was not a LazyFrame. Error: {e}")
        
        # Apply transformations specific to the discharge values
        try:
            discharge_df = (
                df
                .select(pl.col("original_id"), pl.col("datestamp"), pl.col("discharge"))
                .rename({"discharge":"value"})
                .filter((pl.col("value").is_not_null()) & (pl.col("value") != 9999))
                .group_by(["original_id", "datestamp"]).mean()
                .with_columns(qa_id = 0, variable_id = 1)
                .join(self.station_list, on="original_id", how="inner")
                .drop(pl.col("original_id"))
                .select(pl.col("station_id"), pl.col("variable_id").cast(pl.Int8), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8))
            ).collect()
        except pl.exceptions.ColumnNotFoundError as e:
            logger.error(f"Column could not be found or was not expected when transforming discharge data. Error: {e}", exc_info=True)
            raise pl.exceptions.ColumnNotFoundError(f"Column could not be found or was not expected when transforming discharge data. Error: {e}")
        except TypeError as e:
            logger.error(f"TypeError occured, moste likely due to the fact that the station_list was not a LazyFrame. Error: {e}")
            raise TypeError(f"TypeError occured, moste likely due to the fact that the station_list was not a LazyFrame. Error: {e}")
        
        # Set the transformed data
        self._EtlPipeline__transformed_data = {
            "level": [level_df, ["station_id", "datestamp"]],
            "discharge": [discharge_df, ["station_id", "datestamp"]]
        }        

