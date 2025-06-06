from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import(
    ENV_AQN_BASE_URL,
    ENV_AQN_DESTINATION_TABLES,
    ENV_AQN_DTYPE_SCHEMA,
    ENV_AQN_MIN_RATIO,
    ENV_AQN_NAME,
    ENV_AQN_NETWORK_ID,
    ENV_AQN_RENAME_DICT,
    ENV_AQN_STATION_SOURCE
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class EnvAqnPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=ENV_AQN_NAME,
            source_url=ENV_AQN_BASE_URL,
            destination_tables=ENV_AQN_DESTINATION_TABLES,
            days = 3,
            station_source=ENV_AQN_STATION_SOURCE,
            expected_dtype=ENV_AQN_DTYPE_SCHEMA,
            column_rename_dict=ENV_AQN_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=True,
            network_ids= ENV_AQN_NETWORK_ID,
            min_ratio=ENV_AQN_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )


    def transform_data(self):
        """
        Implementation of the transform_data method for the EnvAqnPipeline class. This method will transform the data downloaded from the Environment and Climate Change Canada website, into a format that is ready to be inserted into the database. The main transformation happening here will be the following:
            - Rename Columns
            - Remove rows with null values
            - Filter bad data
            - Join downloaded data with the station list
            - Filter data into different tables

        Args:
            None

        Output:
            None
        """
        logger.info(f"Transforming downloaded data for {self.name}")

        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")

        # TODO: Check for new stations, and insert them into the database if they are new, along with their metadata. Send Email after completion.

        logger.debug(f"Starting Transformation")

        try:
            df = (
                pl.concat([
                    downloaded_data["temperature"],
                    downloaded_data["precipitation"]
                ])
                .rename(self.column_rename_dict)
                # The old scrapers had the following cases for filtering bad data:
                #   - Remove any Null values
                #   - Remove any precipitation values that are less than 0 or greater than or equal to 350 (Since these are hourly values, 350mm of rain would be an absured amount)
                #   - Remove any temperature values that are less than -60 or greater than or equal to 60 degrees Celcius.
                .remove(
                    pl.col("value").is_null() |
                    ((pl.col("value") < 0) & (pl.col("value") >= 350) & (pl.col("variable")== "PRECIP")) |
                    ((pl.col("value") <= -60) & (pl.col("value") >= 60) & (pl.col("variable")== "TEMP"))
                )
                .with_columns(
                    datestamp = (pl
                        .col("datestamp")
                        .str.to_datetime("%Y-%m-%d %H:%M", time_zone="America/Vancouver")
                        .dt.date()
                    ),
                    variable_id = (pl
                        .when(pl.col("variable") == "TEMP")
                        .then(pl.lit(7))
                        .when(pl.col("variable") == "PRECIP")
                        .then(pl.lit(27))
                    ),
                    qa_id = pl.lit(0)
                )
                .filter(
                    pl.col("datestamp") >= self.start_date.date()
                )
                .join(self.station_list, on="original_id", how="inner")
                .select(
                    "station_id",
                    "variable_id",
                    "datestamp",
                    "value",
                    "qa_id"
                )
            ).collect()
        except Exception as e:
            logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")

        # Make separate dataframes for the different tables that it will get inserted into
        try:
            df_temp = pl.concat([
                (
                    df
                    .filter(pl.col("variable_id") == pl.lit(7))
                    .with_columns(variable_id = pl.lit(6))
                    .group_by(["station_id", "datestamp", "qa_id", "variable_id"]).max()
                ),
                (
                    df
                    .filter(pl.col("variable_id") == pl.lit(7))
                    .group_by(["station_id", "datestamp", "qa_id", "variable_id"]).mean()
                ),
                (
                    df
                    .filter(pl.col("variable_id") == pl.lit(7))
                    .with_columns(variable_id = pl.lit(8))
                    .group_by(["station_id", "datestamp", "qa_id", "variable_id"]).min()
                )
            ])

        except Exception as e:
            logger.error(f"Error when constructing the insertion table for Temperature", exc_info=True)
            raise RuntimeError(f"Error when constructing the insertion table for Temperature. Error: {e}")

        try:
            df_precip = (
                df
                .filter(pl.col("variable_id") == pl.lit(27))
                .group_by(["station_id", "datestamp", "qa_id", "variable_id"]).sum()
            )
        except Exception as e:
            logger.error(f"Error when constructing the insertion table for Precipitation", exc_info=True)
            raise RuntimeError(f"Error when constructing the insertion table for Precipitation. Error: {e}")

        self._EtlPipeline__transformed_data = {
            "temperature": {"df": df_temp, "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False},
            "precipitation": {"df": df_precip, "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False}
        }

        logger.info(f"Finished Transforming data for {self.name}")

    def get_and_insert_new_stations(self, station_data=None):
        pass
