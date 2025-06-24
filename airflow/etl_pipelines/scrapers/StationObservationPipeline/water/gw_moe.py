from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    MOE_GW_BASE_URL,
    MOE_GW_NETWORK,
    MOE_GW_NAME,
    MOE_GW_DESTINATION_TABLES,
    MOE_GW_STATION_SOURCE,
    MOE_GW_DTYPE_SCHEMA,
    MOE_GW_RENAME_DICT,
    MOE_GW_MIN_RATIO,
    QUARTERLY_MOE_GW_BASE_URL,
    QUARTERLY_MOE_GW_DTYPE_SCHEMA,
    QUARTERLY_MOE_GW_NAME,
    QUARTERLY_MOE_GW_RENAME_DICT,
    QUARTERLY_MOE_GW_MIN_RATIO,
    SPRING_DAYLIGHT_SAVINGS
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class GwMoePipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now = None, quarterly = False):
        """
        The code for the quarterly MOE GW update is bascially the same from the daily scraper. Some minor changes
        are needed so they are controled by this self.quarterly flag.
        For instance, there are slight differences to the initialization of the class, so it is controlled by the flag.
        """
        self.quarterly = quarterly

        if not quarterly:
            super().__init__(
                name=MOE_GW_NAME,
                source_url=[],
                destination_tables=MOE_GW_DESTINATION_TABLES,
                days=2,
                station_source=MOE_GW_STATION_SOURCE,
                expected_dtype=MOE_GW_DTYPE_SCHEMA,
                column_rename_dict=MOE_GW_RENAME_DICT,
                go_through_all_stations=True,
                overrideable_dtype=True,
                network_ids= MOE_GW_NETWORK,
                min_ratio=MOE_GW_MIN_RATIO,
                db_conn=db_conn,
                date_now=date_now
            )

            self.source_url = {original_id: MOE_GW_BASE_URL.format(original_id) for original_id in self.station_list.collect()["original_id"].to_list()}
        else:
            super().__init__(
                name=QUARTERLY_MOE_GW_NAME,
                source_url=[],
                destination_tables = MOE_GW_DESTINATION_TABLES,
                days = 2,
                station_source=MOE_GW_STATION_SOURCE,
                expected_dtype=QUARTERLY_MOE_GW_DTYPE_SCHEMA,
                column_rename_dict=QUARTERLY_MOE_GW_RENAME_DICT,
                go_through_all_stations=True,
                overrideable_dtype=True,
                network_ids= MOE_GW_NETWORK,
                min_ratio=QUARTERLY_MOE_GW_MIN_RATIO,
                db_conn=db_conn,
                date_now=date_now
            )

            self.source_url = {original_id: QUARTERLY_MOE_GW_BASE_URL.format(original_id) for original_id in self.station_list.collect()["original_id"].to_list()}



    def transform_data(self):
        """
        Implementation of the transform_data Method for the class GwMoePipeline. This contains all the data for the gw_moe stations, and can be transformed all together and inserted all together as well. The main transformation happening here will be the following:
            - Rename Columns
            - Drop Columns
            - Group them by date and station_id, while taking the average of the values.

        When it is running the quarterly version, the datasource does not have a `Approval` column, so we create one with all `Approved` values so that the `qa_id = 1`. In addition, unlike the daily scraper, we want to import all data for all dates, so no date is filtered.
        The group by in the quarterly case does nothing, datestamp and station_id is already a key of the dataframe.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Startion Transformation of {self.name}")

        # Get downloaded lazy dataframe from the private attribute using getter function
        downloaded_data = self.get_downloaded_data()

        # Check that the downloaded data is not empty. If it is, something went wrong since it passed validation.
        if not downloaded_data:
            logger.error("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")
            raise RuntimeError("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")

        # Transform data
        try:
            df = downloaded_data["station_data"]
        except KeyError as e:
            logger.error(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key station_data was not found, or the entered key was incorrect.", exc_info=True)
            raise KeyError(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key station_data was not found, or the entered key was incorrect. Error: {e}")

        # apply some transformations that will be done to both the dataframes:
        total_station_with_data = df.collect().n_unique("myLocation")
        try:
            df = (
                df
                .rename(self.column_rename_dict)
                .remove(pl.col("datestamp").is_in(SPRING_DAYLIGHT_SAVINGS))
                .with_columns(
                    datestamp = pl.col("datestamp").str.slice(offset=0, length=10).str.to_date("%Y-%m-%d"),
                    Approval = (pl.lit("Approved") if self.quarterly else pl.col("Approval")),
                )
                .filter(
                    # If it's a quarterly run then we want to include ALL dates. Hence the OR
                    ((pl.col("datestamp") >= self.start_date.dt.date()) | (self.quarterly)) &
                    ((pl.col("datestamp") < self.end_date.dt.date()) | (self.quarterly)) &
                    (pl.col("value").is_not_null()) &
                    (pl.col("value") < 2000)
                )
                .with_columns(
                    qa_id =(pl
                        .when(pl.col('Approval').is_in(["Approved", "Validated"]))
                        .then(1)
                        .otherwise(0)
                    ),
                    variable_id = 3,
                    value = (pl
                        .when(pl.col("value") < 0)
                        .then(0)
                        .otherwise(pl.col("value"))
                    )
                )
                .group_by(["datestamp", "original_id", "variable_id"]).agg([pl.mean("value"), pl.min("qa_id")])
                .join(self.station_list, on="original_id", how="inner")
                .select(
                    pl.col("station_id"),
                    pl.col("datestamp"),
                    pl.col("value"),
                    pl.col("variable_id").cast(pl.Int8),
                    pl.col("qa_id").cast(pl.Int8)
                )
            ).collect()

        except pl.exceptions.ColumnNotFoundError as e:
            logger.error(f"Column could not be found or was not expected when transforming groundwater data. Error: {e}", exc_info=True)
            raise pl.exceptions.ColumnNotFoundError(f"Column could not be found or was not expected when transforming groundwater data. Error: {e}")
        except TypeError as e:
            logger.error(f"TypeError occured, moste likely due to the fact that the station_list was not a LazyFrame. Error: {e}")
            raise TypeError(f"TypeError occured, moste likely due to the fact that the station_list was not a LazyFrame. Error: {e}")

        # There is a Issue to fix this, as well as add the missing stations. Currently there are 250 or so stations that are "allgedly" reporting data. We only have 100 or so of them. The GH issue #61 will deal with this.
        logger.info(f"""NOTE: Out of the {total_station_with_data} stations that returned a 200 response and was not emtpy csv files only {df.n_unique("station_id")} stations had recent data (within the last 2 days)""")

        self._EtlPipeline__transformed_data = {
            "gw_level" : {"df": df, "pkey": ["station_id", "datestamp"], "truncate": False}
        }

        logger.info(f"Transformation complete for Groundwater Level")
    def get_and_insert_new_stations(self, station_data = None):
        pass
