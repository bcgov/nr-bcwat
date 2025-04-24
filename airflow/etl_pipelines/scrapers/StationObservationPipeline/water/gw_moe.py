from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    MOE_GW_BASE_URL,
    MOE_GW_NETWORK,
    MOE_GW_NAME,
    MOE_GW_DESTINATION_TABLES,
    MOE_GW_STATION_SOURCE,
    MOE_GW_DTYPE_SCHEMA,
    MOE_GW_RENAME_DICT,
    SPRING_DAYLIGHT_SAVINGS
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class GwMoePipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now = None):
        super().__init__(name=MOE_GW_NAME, source_url=[], destination_tables=MOE_GW_DESTINATION_TABLES)
        

        ## Add Implementation Specific attributes below
        self.days = 2
        self.network = MOE_GW_NETWORK
        self.station_source = MOE_GW_STATION_SOURCE
        self.expected_dtype = MOE_GW_DTYPE_SCHEMA
        self.column_rename_dict = MOE_GW_RENAME_DICT
        self.go_through_all_stations = True
        
        self.db_conn = db_conn

        self.date_now = date_now.in_tz("UTC")

        self.end_date = self.date_now.in_tz("America/Vancouver")
        self.start_date = self.end_date.subtract(days=self.days).start_of("day")
        
        ## get_station_list() is called earlier here since the download URL depends on self.station_list
        self.get_station_list()
        station_list_materialized = self.station_list.collect()["original_id"].to_list()
        self.source_url = {original_id: MOE_GW_BASE_URL.format(original_id) for original_id in station_list_materialized}



    def transform_data(self):
        """
        Implementation of the transform_data Method for the class GwMoePipeline. This contains all the data for the gw_moe stations, and can be transformed all together and inserted all together as well. The main transformation happening here will be the following:
            - Rename Columns
            - Drop Columns
            - Group them by date and station_id, while taking the average of the values.

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
                .with_columns(pl.col("datestamp").str.to_datetime("%Y-%m-%d %H:%M", time_zone="America/Vancouver", ambiguous="earliest"))
                .filter((pl.col("datestamp") > self.start_date) & (pl.col("value").is_not_null()) & (pl.col("value") < 2000))
                .with_columns(
                    qa_id = pl.when(
                        pl.col('Approval').is_in(["Approved", "Validated"]))
                            .then(1)
                            .otherwise(0),
                    variable_id = 3,
                    datestamp = pl.col("datestamp").dt.date()
                )
                .group_by(["datestamp", "original_id"]).agg([pl.mean("value"), pl.min("qa_id"), pl.min("variable_id")])
                .join(self.station_list, on="original_id", how="inner")
                .select(pl.col("station_id"), pl.col("variable_id").cast(pl.Int8), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8))
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
            "gw_level" : [df, ["station_id", "datestamp"]]
        }

        logger.info(f"Transformation complete for Groundwater Level")
