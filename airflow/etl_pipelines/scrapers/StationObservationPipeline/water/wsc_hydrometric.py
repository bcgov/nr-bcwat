from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    WSC_NAME,
    WSC_NETWORK,
    WSC_URL,
    WSC_DESTINATION_TABLES,
    WSC_STATION_SOURCE,
    WSC_DTYPE_SCHEMA,
    WSC_RENAME_DICT,
    WSC_MIN_RATIO
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class WscHydrometricPipeline(StationObservationPipeline):
    def __init__(self, db_conn = None, date_now = None, days=2):
        # Initializing attributes in parent class
        super().__init__(
            name=WSC_NAME,
            source_url=[],
            destination_tables=WSC_DESTINATION_TABLES,
            days=days,
            station_source=WSC_STATION_SOURCE,
            expected_dtype=WSC_DTYPE_SCHEMA,
            column_rename_dict=WSC_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=True,
            network_ids= WSC_NETWORK,
            min_ratio=WSC_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )

        self.source_url = {"wsc_daily_hydrometric.csv": WSC_URL.format(self.date_now.strftime("%Y%m%d"))}



    def transform_data(self):
        """
        Implementation of the transform_data method for the class WscHydrometricPipeline. Since the downloaded data contains two different kinds of data that will be inserted into two separate tables of the database, common transformations have been made before splitting the data into two different dataframes. After which, the dataframes are transformed to match the schema of the database tables.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Starting Transformation step")
        # Get the downloaded data
        downloaded_data_list = self.get_downloaded_data()

        # Check if there is any downloaded data if not raise an error
        if not downloaded_data_list:
            logger.error("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")
            raise RuntimeError("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")

        # Transform the data
        try:
            df = downloaded_data_list["wsc_daily_hydrometric.csv"]
        except KeyError as e:
            logger.error(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect.", exc_info=True)
            raise KeyError(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect. Error: {e}")

        # apply some transformations that will be done to both the dataframes:
        try:
            df = (
                df
                .rename(self.column_rename_dict)
                .select(self.column_rename_dict.values())
                .with_columns((pl.col("datestamp").str.to_datetime("%Y-%m-%dT%H:%M:%S%:z")).alias("datestamp"))
                .filter(
                    (pl.col("datestamp").dt.date() >= self.start_date.dt.date()) &
                    (pl.col("datestamp").dt.date() < self.end_date.dt.date())
                )
                .with_columns(pl.col("datestamp"))
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
            "station_data": {"df": pl.concat([level_df, discharge_df]), "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False}
        }

        logger.info(f"Transformation complete for Level and Discharge data")

    def get_and_insert_new_stations(self, station_data = None):
        pass
