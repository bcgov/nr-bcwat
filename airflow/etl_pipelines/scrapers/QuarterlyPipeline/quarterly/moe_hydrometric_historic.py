from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA,
    QUARTERLY_MOE_HYDRO_HIST_BASE_URL,
    QUARTERLY_MOE_HYDRO_HIST_DESTINATION_TABLES,
    QUARTERLY_MOE_HYDRO_HIST_NAME,
    QUARTERLY_MOE_HYDRO_HIST_RENAME_DICT,
    QUARTERLY_MOE_HYDRO_HIST_NETWORK_ID,
    HEADER,
    SPRING_DAYLIGHT_SAVINGS
)
from etl_pipelines.utils.functions import setup_logging
from bs4 import BeautifulSoup
import pendulum
import polars as pl
import re
import requests

logger = setup_logging()

class QuarterlyMoeHydroHistoricPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=pendulum.now("UTC"), archive_type="discharge"):
        super().__init__(
            name=QUARTERLY_MOE_HYDRO_HIST_NAME,
            source_url={},
            destination_tables=QUARTERLY_MOE_HYDRO_HIST_DESTINATION_TABLES,
            days=2,
            station_source='',
            expected_dtype=QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA,
            column_rename_dict=QUARTERLY_MOE_HYDRO_HIST_RENAME_DICT,
            go_through_all_stations=True,
            overrideable_dtype = True,
            network_ids=QUARTERLY_MOE_HYDRO_HIST_NETWORK_ID,
            min_ratio={},
            db_conn=db_conn,
            date_now=date_now
        )
        self.get_all_stations_in_network()

        logger.info(f"Running {archive_type} Historical records update for {self.name}")

        self.archive_type = archive_type

        self.__get_all_source_urls()

    def transform_data(self):
        """
        Transforms the downloaded hydrometric data for historical records into a format suitable for database insertion.
        The transformation process includes:
        - Renaming columns based on the provided dictionary.
        - Adjusting the `datestamp` column to exclude entries during spring daylight savings and formatting it to a specific datetime format.
        - Calculating `qa_id` based on data quality.
        - Determining `variable_id` for `Discharge` and `Stage` parameters.
        - Converting `value` to appropriate units.
        - Filtering out rows with NaN values.
        - Joining the transformed data with station information from the network.
        - Grouping data by `station_id`, `datestamp`, `variable_id`, and `symbol_id` and aggregating to compute mean `value` and minimum `qa_id`.
        - Selecting and casting relevant columns for the final data structure.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Starting Transformation for {self.name}")
        downloaded_data = self.get_downloaded_data()["station_data"]

        try:
            data = (
                downloaded_data
                .rename(self.column_rename_dict)
                .with_columns(
                    datestamp = pl.col("datestamp").str.slice(offset=0, length=16)
                )
                .remove(pl.col("datestamp").is_in(SPRING_DAYLIGHT_SAVINGS))
                .with_columns(
                    datestamp = pl.col("datestamp").str.to_datetime("%Y-%m-%d %H:%M", time_zone="UTC", ambiguous="earliest").dt.date(),
                    qa_id = (pl
                    .when(pl.col('Grade').str.to_lowercase() == "unusable")
                        .then(0)
                        .otherwise(1)
                    ),
                    variable_id = (pl
                        .when(pl.col("Parameter") == "Discharge")
                        .then(1)
                        .otherwise(2)
                    ),
                    value = (pl
                        .when((pl.col("Parameter") == "Discharge") & (pl.col("Unit") == "l/s")).then(pl.col("value").cast(pl.Float64) / 1000) # Convert to m^3/s
                        .when((pl.col("Parameter") == "Stage") & (pl.col("Unit") == "cm")).then(pl.col("value").cast(pl.Float64)/100) # Convert to m
                        .otherwise(pl.col("value").cast(pl.Float64))),
                    symbol_id = pl.lit(None).cast(pl.Int16)
                )
                .remove(pl.col("value").is_nan())
                .join(
                    other=self.all_stations_in_network,
                    on="original_id",
                    how="inner"
                )
                .group_by("station_id", "datestamp", "variable_id", "symbol_id")
                .agg(
                    pl.col("value").mean(),
                    pl.col("qa_id").min()
                )
                .select(
                    pl.col("station_id"),
                    pl.col("datestamp"),
                    pl.col("value"),
                    pl.col("qa_id").cast(pl.Int8),
                    pl.col("variable_id").cast(pl.Int8),
                    pl.col("symbol_id")
                )
            ).collect()
        except Exception as e:
            logger.error(f"Failed to materialize the LazyFrame with all the transformations applied. Please check the error and retry. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to materialize the LazyFrame with all the transformations applied. Please check the error and retry. Error: {e}")

        self._EtlPipeline__transformed_data[self.archive_type] = {"df": data, "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False}

        logger.info(f"Finished Transformation for {self.name}")

    def get_and_insert_new_stations(self):
        """
        Checks for new stations in the downloaded data and inserts them into the database. Also checks if they are in BC and if so, inserts them into the database.

        Args:
            None

        Output:
            None
        """
        logger.info("Getting new stations and inserting them into the database")

        try:
            new_station = (
                self.get_downloaded_data()["station_data"]
                .rename(self.column_rename_dict)
                .join(
                    other=self.all_stations_in_network,
                    on="original_id",
                    how="anti"
                )
                .with_columns(
                    pl.col("station_name").str.to_titlecase()
                )
                .select(
                    "original_id",
                    "station_name",
                    "longitude",
                    "latitude"
                )
                .unique()
            )

            if new_station.limit(1).collect().is_empty():
                logger.info("No new stations found, continuing on with transformation")
                return

        except Exception as e:
            logger.error(f"Error when trying to check for new stations. Please check the error and retry. Error:{e}", exc_info=True)
            raise RuntimeError(f"Error when trying to check for new stations. Please check the error and retry. Error:{e}")

        logger.info(f"Found {new_station.collect().shape[0]} new stations. Checking if they are in BC")

        try:
            in_bc_list = self.check_new_station_in_bc(new_station.select("original_id", "longitude", "latitude"))
        except Exception as e:
            logger.error(f"Error when trying to check if new stations are in BC. Please check the error and retry. Error:{e}", exc_info=True)
            raise RuntimeError(f"Error when trying to check if new stations are in BC. Please check the error and retry. Error:{e}")

        if len(in_bc_list) == 0:
            logger.info("No new stations found in BC, continuing on with transformation")
            return

        new_station = (
            new_station
            .filter(pl.col("original_id").is_in(in_bc_list))
            .with_columns(
                station_status_id = pl.lit(1),
                scrape = pl.lit(False),
                stream_name = pl.lit(None).cast(pl.String),
                station_description = pl.lit(None).cast(pl.String),
                operation_id = pl.lit(None).cast(pl.Int64),
                drainage_area = pl.lit(None).cast(pl.Float32),
                regulated = pl.lit(False),
                user_flag = pl.lit(False),
                year = pl.lit([2025]).cast(pl.List(pl.Int64)),
                project_id = [6],
                network_id = 53,
                type_id = 1,
                variable_id = (pl
                    .when(pl.lit(self.archive_type) == pl.lit("Discharge")).then([1])
                    .otherwise([2])
                )
            )
            .select(
                "original_id",
                "station_name",
                "station_status_id",
                "longitude",
                "latitude",
                "scrape",
                "stream_name",
                "station_description",
                "operation_id",
                "drainage_area",
                "regulated",
                "user_flag",
                "year",
                "project_id",
                "network_id",
                "type_id",
                "variable_id"
            )
        )

        try:
            new_station, other_metadata_dict = self.construct_insert_tables(new_station)
        except Exception as e:
            logger.error(f"Error when trying to construct insert tables. Please check the error and retry. Error:{e}", exc_info=True)
            raise RuntimeError(f"Error when trying to construct insert tables. Please check the error and retry. Error:{e}")

        try:
            self.insert_new_stations(new_station, other_metadata_dict)
        except Exception as e:
            logger.error(f"Error when trying to insert new stations. Please check the error and retry. Error:{e}", exc_info=True)
            raise RuntimeError(f"Error when trying to insert new stations. Please check the error and retry. Error:{e}")

        logger.info("Finished getting new stations and inserting them into the database")

    def __get_all_source_urls(self):
        """
        Private method to get all the source urls for the given archive type (either "Discharge" or "Stage").
        This method will go to the base url, parse the html, and find all the links in the page.
        It will then loop through all the links and if the link is a csv file that contains the archive type,
        it will add it to the source_url dictionary with the key being the filename and the value being the full url.

        Args:
            None

        Output:
            None
        """
        r = requests.get(QUARTERLY_MOE_HYDRO_HIST_BASE_URL, headers=HEADER)
        soup = BeautifulSoup(r.text, features="html.parser")
        table = soup.find("table")
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("a")
            for ele in cols:
                m = re.match(f"{self.archive_type}.*csv", ele.get("href"))
                if m is not None:
                    self.source_url[m.group()] = QUARTERLY_MOE_HYDRO_HIST_BASE_URL + m.group()
