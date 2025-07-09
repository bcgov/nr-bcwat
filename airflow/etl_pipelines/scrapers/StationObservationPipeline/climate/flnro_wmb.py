from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    ENV_FLNRO_WMB_STATION_SOURCE,
    ENV_FLNRO_WMB_BASE_URL,
    ENV_FLNRO_WMB_DESTINATION_TABLES,
    ENV_FLNRO_WMB_DTYPE_SCHEMA,
    ENV_FLNRO_WMB_NAME,
    ENV_FLNRO_WMB_NETWORK_ID,
    ENV_FLNRO_WMB_RENAME_DICT,
    ENV_FLNRO_WMB_MIN_RATIO,
    NEW_STATION_MESSAGE_FRAMEWORK
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class FlnroWmbPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=ENV_FLNRO_WMB_NAME,
            source_url={},
            destination_tables=ENV_FLNRO_WMB_DESTINATION_TABLES,
            days=3,
            station_source=ENV_FLNRO_WMB_STATION_SOURCE,
            expected_dtype=ENV_FLNRO_WMB_DTYPE_SCHEMA,
            column_rename_dict=ENV_FLNRO_WMB_RENAME_DICT,
            go_through_all_stations=True,
            overrideable_dtype=True,
            network_ids=ENV_FLNRO_WMB_NETWORK_ID,
            min_ratio=ENV_FLNRO_WMB_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )

        ## Add Implementation Specific attributes below
        date_list = [date_now.subtract(days=x) for x in range(self.days)]
        self.source_url = {date.strftime("%Y-%m-%d"): ENV_FLNRO_WMB_BASE_URL.format(date.year, date.strftime("%Y-%m-%d")) for date in date_list}

    def transform_data(self):
        """
        Transforms the downloaded data for the FLNRO-WMB PCIC pipeline into a format suitable for database insertion.

        This method performs various transformations on the downloaded station data, including:
        - Renaming columns based on a predefined dictionary.
        - Unpivoting the data to align with the database schema.
        - Removing rows with null values.
        - Padding datestamp strings to ensure proper datetime conversion.
        - Converting datestamp to a datetime object and adjusting its timezone.
        - Mapping variable names to their corresponding variable IDs.
        - Joining the transformed data with the station list to get station IDs.

        After transformation, the data is split into separate dataframes for temperature and precipitation,
        grouped and aggregated accordingly.

        Args:
            None

        Output: None
        """

        logger.info(f"Transforming downloaded data for {self.name}")

        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")

        try:
            new_stations = self.check_for_new_stations().collect()

            if new_stations.is_empty():
                logger.info(f"There are no new stations in the data downloaded for {self.name}. Continuing on")
            else:
                logger.warning(NEW_STATION_MESSAGE_FRAMEWORK.format(self.name, ", ".join(new_stations["original_id"].to_list()), "BC Government: Ministry of Forests", "Please check that the stations are within BC before inserting.", self.name, ", ".join(self.network)))
        except Exception as e:
            logger.error(f"Failed to get new stations from the data downloaded for {self.name}. Moving on without inserting new stations.")

        logger.debug(f"Starting Transformation")

        df = downloaded_data["station_data"]

        try:
            df = (
                df
                .rename(self.column_rename_dict)
                .select(list(self.column_rename_dict.values()))
                .unpivot(index=["original_id", "datestamp"])
                .remove(pl.col("value").is_null())
                # Add "00" to the end of the datestamp strings since the to_datetime function requires BOTH hour and minute, not either or.
                # The current format is: YYYYMMDDHH. This will make it YYYYMMDDHHmm
                .with_columns(
                    datestamp = pl.col("datestamp").str.pad_end(12, "0")
                )
                .with_columns(
                    datestamp = (pl
                        .col("datestamp")
                        .str.to_datetime("%Y%m%d%H%M", time_zone = "UTC")
                        .dt.date()
                    ),
                    variable_id = (pl
                        .when(pl.col("variable") == "temperature_hourly")
                        .then(pl.lit(7))
                        .when(pl.col("variable") == "precipitation_hourly")
                        .then(pl.lit(27))
                    ),
                    qa_id = pl.lit(0)

                )
                .filter(
                    (pl.col("datestamp") >= self.start_date.dt.date()) &
                    (pl.col("datestamp") < self.end_date.dt.date())
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
            "station_data": {"df": pl.concat([df_temp, df_precip]), "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False},
        }

        logger.info(f"Finished Transforming data for {self.name}")
