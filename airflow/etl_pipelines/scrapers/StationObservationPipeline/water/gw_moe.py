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
    MOE_GW_NEW_STATION_URL,
    QUARTERLY_MOE_GW_BASE_URL,
    QUARTERLY_MOE_GW_DTYPE_SCHEMA,
    QUARTERLY_MOE_GW_NAME,
    QUARTERLY_MOE_GW_RENAME_DICT,
    QUARTERLY_MOE_GW_MIN_RATIO,
    SPRING_DAYLIGHT_SAVINGS,
    HEADER,
    MAX_NUM_RETRY
)
from etl_pipelines.utils.functions import setup_logging
from time import sleep
import polars as pl
import os
import requests
import zipfile


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
            self.file_path = "data/"

            self.source_url = {original_id: MOE_GW_BASE_URL.format(original_id) for original_id in self.station_list.collect()["original_id"].to_list()}
        else:
            super().__init__(
            name=QUARTERLY_MOE_GW_NAME,
                source_url=[],
                destination_tables = MOE_GW_DESTINATION_TABLES,
                days = 365,
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
        logger.info(f"""NOTE: Out of the {total_station_with_data} stations that returned a 200 response and was not emtpy csv files only {df.n_unique("station_id")} stations had recent data (within the last {self.days} days)""")

        self._EtlPipeline__transformed_data = {
            "station_data" : {"df": df, "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False}
        }

        logger.info(f"Transformation complete for Groundwater Level")

    def get_and_insert_new_stations(self):
        """
        Method to get and insert new stations from the gw_wells.zip folder that gets downloaded. Since this is zipped, it will get extracted and and saved to a PVC.
        After extractions, the wells.csv file is read and several checks are completed:
            - Check if there are new stations in the downloaded data
            - Check if the new stations are within BC
            - Construct the LazyFrames that will be inserted in to the database
            - Insert the stations in to the database.
        Once the insertion is complete, it will move on to the download step for the scraper.

        If an error occurs, then the error will be logged, and the scraper will move on to scraping without adding the new stations.

        Args:
        """

        logger.info(f"Starting process of checking for new stations for {self.name}")

        logger.debug(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")

        while True:
            try:
                response = requests.get(MOE_GW_NEW_STATION_URL, stream=True, timeout=5)
            except Exception as e:
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Error downloading MOE GW station list from URL: {MOE_GW_NEW_STATION_URL}. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(5)
                    continue
                else:
                    logger.error(f"Failed to download MOE GW station list from {MOE_GW_NEW_STATION_URL}. Raising Error {e}", exc_info=True)
                    raise RuntimeError(f"Failed to download MOE GW station list from {MOE_GW_NEW_STATION_URL}. Error {e}")

            if response.status_code != 200:
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Response status was not 200. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(5)
                    continue
                else:
                    logger.error(f"Response status was not 200 when trying to download MOE GW station list.")
                    raise RuntimeError(f"Response status was not 200 when trying to download MOE GW station list.")
            break

        # Used to prevent loading the response to memory all at once.
        try:
            with open(os.path.join(self.file_path, MOE_GW_NEW_STATION_URL.split("/")[-1]), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            logger.error(f"Failed when trying to write the chunked zipped MOE GW station list file to disk. Error {e}", exc_info=True)
            raise IOError(f"Failed when trying to write the chunked zipped MOE GW station list file to disk. Error {e}")

        # Used to use the CLI unzip tool but this should suffice
        try:
            with zipfile.ZipFile(os.path.join(self.file_path, MOE_GW_NEW_STATION_URL.split("/")[-1]), "r") as zip_ref:
                zip_ref.extractall(self.file_path)
        except Exception as e:
            logger.error(f"Failed when trying to unzip the MOE GW station list file. Error {e}", exc_info=True)
            raise IOError(f"Failed when trying to unzip the MOE GW station list file. Error {e}")

        logger.debug(f"Finished Unzipping MOE GW station list")

        self.get_all_stations_in_network()

        try:

            well_data = (
                pl.scan_csv(os.path.join(self.file_path, "well.csv"), infer_schema=False)
                .filter(
                    (pl.col("observation_well_number").is_not_null()) &
                    (pl.col("obs_well_status_code") == pl.lit("Active"))
                )
                .rename({"observation_well_number": "original_id"})
                .join(
                    other=self.all_stations_in_network,
                    on="original_id",
                    how="anti"
                )
            )

            if well_data.limit(1).collect().is_empty():
                logger.info("No new active stations were found in the station list. Continuing on without inserting.")
                return

            in_bc = self.check_new_station_in_bc(well_data.select("original_id", "longitude_Decdeg", "latitude_Decdeg"))

            # Filter out water_supply_system_name and water_supply_system_well_name is both null because then there will be no stations name
            well_data = (
                well_data
                .filter(
                    (pl.col("original_id").is_in(in_bc)) &
                    ((pl.col("water_supply_system_name").is_not_null()) | pl.col("water_supply_system_well_name").is_not_null())
                )
            )

            if well_data.limit(1).collect().is_empty():
                logger.info("No new active stations in BC were found. Continuing on without inserting.")
                return

        except Exception as e:
            logger.error(f"Failed to check for new stations in BC from the MOE GW station list dataset! Continuing without checking for new stations. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to check for new stations in BC from the MOE GW station list dataset! Continuing without checking for new stations. Error: {e}")

        try:
            logger.debug("Constructing LazyFrames to insert in to the database")

            well_data = (
                well_data
                .with_columns(
                    type_id = 2,
                    variable_id = [3],
                    project_id = [6],
                    network_id = 10,
                    station_status_id = 4,
                    scrape = pl.lit(True),
                    regulated = pl.lit(False),
                    user_flag = pl.lit(False),
                    year = self.date_now.year,
                    station_name = (pl
                        .when(pl.col("water_supply_system_name").is_not_null() & pl.col("water_supply_system_well_name").is_not_null())
                        .then(pl.col("water_supply_system_name").str.to_titlecase() + pl.lit(" (") + pl.col("water_supply_system_well_name").str.to_titlecase() + pl.lit(")"))
                        .when(pl.col("water_supply_system_name").is_null() & pl.col("water_supply_system_well_name").is_not_null())
                        .then(pl.col("water_supply_system_well_name").str.to_titlecase())
                        .when(pl.col("water_supply_system_name").is_not_null() & pl.col("water_supply_system_well_name").is_null())
                        .then(pl.col("water_supply_system_name").str.to_titlecase())
                        .otherwise(pl.lit(None).cast(pl.String))
                    ),
                    station_description = pl.lit(None).cast(pl.String),
                    stream_name = pl.lit(None).cast(pl.String),
                    operation_id = 3,
                    drainage_area = pl.lit(None).cast(pl.Float32)
                )
                .select(
                    pl.col("original_id"),
                    pl.col("station_name"),
                    pl.col("station_status_id"),
                    pl.col("longitude_Decdeg").alias("longitude"),
                    pl.col("latitude_Decdeg").alias("latitude"),
                    pl.col("scrape"),
                    pl.col("stream_name"),
                    pl.col("station_description"),
                    pl.col("operation_id"),
                    pl.col("drainage_area"),
                    pl.col("regulated"),
                    pl.col("user_flag"),
                    pl.col("year"),
                    pl.col("project_id"),
                    pl.col("network_id"),
                    pl.col("type_id"),
                    pl.col("variable_id")
                )
            )
            well_data, metadata = self.construct_insert_tables(well_data)

        except Exception as e:
            logger.error(f"Failed to build LazyFrame to insert into the database for new stations. Continuing without inserting new stations. Error{e}", exc_info=True)
            raise RuntimeError(f"Failed to build LazyFrame to insert into the database for new stations. Continuing without inserting new stations. Error{e}")

        try:
            self.insert_new_stations(well_data, metadata)
        except Exception as e:
            logger.error(f"Failed inserting new stations and related metadata in to the database. Continuing without inserting. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed inserting new stations and related metadata in to the database. Continuing without inserting. Error: {e}")
