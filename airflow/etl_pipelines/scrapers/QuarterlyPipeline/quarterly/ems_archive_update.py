from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    HEADER,
    QUARTERLY_EMS_CURRENT_URL,
    QUARTERLY_EMS_HISTORICAL_URL,
    QUARTERLY_EMS_DESTINATION_TABLES,
    QUARTERLY_EMS_DTYPE_SCHEMA,
    QUARTERLY_EMS_RENAME_DICT,
    QUARTERLY_EMS_NAME,
    QUARTERLY_EMS_NETWORK_ID,
    QUARTERLY_EMS_DATABC_LAYER,
    QUARTERLY_EMS_COLS_TO_KEEP,
    QUARTERLY_EMS_MIN_RATIO,
    NEW_EMS_LOCATION_TYPE_CODE_MESSAGE,
    STATION_NAME_LOWER_TO_UPPER_CASE_DICT,
    MAX_NUM_RETRY
)
from etl_pipelines.utils.functions import setup_logging
from etl_pipelines.utils.ChemistryNlp import NLP
from time import sleep
from psycopg2.extras import execute_values
import polars as pl
import polars_st as st
import pendulum
import requests
import os
import zipfile
import bcdata

logger = setup_logging()

class QuarterlyEmsArchiveUpdatePipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=pendulum.now("UTC")):
        super().__init__(
            name=QUARTERLY_EMS_NAME,
            source_url=QUARTERLY_EMS_CURRENT_URL,
            destination_tables=QUARTERLY_EMS_DESTINATION_TABLES,
            days=2,
            station_source='',
            expected_dtype=QUARTERLY_EMS_DTYPE_SCHEMA,
            column_rename_dict=QUARTERLY_EMS_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype = False,
            network_ids=QUARTERLY_EMS_NETWORK_ID,
            min_ratio=QUARTERLY_EMS_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )
        self.file_path = "airflow/data/"
        self.csv_path = "airflow/data/ems_sample_results_historic_expanded.csv"
        self.databc_layer_name = QUARTERLY_EMS_DATABC_LAYER
        self.historical_source = QUARTERLY_EMS_HISTORICAL_URL

    def download_historical_data(self):
        """
        Method that downloads the quarterly hydrometric historical archive data from the historical source URL.
        The method will keep retrying until it successfully downloads the data, or until it reaches the maximum number of retries.

        Args:
            None

        Output:
            None
        """

        logger.info(f"Downloading zipped EMS data from {self.historical_source}")

        while True:
            try:
                response = requests.get(self.historical_source, stream=True, headers=HEADER, timeout=20)
            except Exception as e:
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Error downloading EMS data from URL: {self.historical_source}. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(5)
                    continue
                else:
                    logger.error(f"Failed to download EMS data from {self.historical_source}. Raising Error {e}", exc_info=True)
                    raise RuntimeError(f"Failed to download EMS data from {self.historical_source}. Error {e}")

            if response.status_code != 200:
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Response status was not 200. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(5)
                    continue
                else:
                    logger.error(f"Response status was not 200 when trying to download EMS data. Raising Error {e}", exc_info=True)
                    raise RuntimeError(f"Response status was not 200 when trying to download EMS data. Error {e}")
            break

        # Used to prevent loading the response to memory all at once.
        try:
            with open(os.path.join(self.file_path, self.historical_source.split("/")[-1]), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            logger.error(f"Failed when trying to write the chunked zipped EMS data file to disk. Error {e}", exc_info=True)
            raise IOError(f"Failed when trying to write the chunked zipped EMS data file to disk. Error {e}")

        logger.info(f"Finished downloading EMS data, Unzipping the Zip file")

        # Used to use the CLI unzip tool but this should suffice
        try:
            with zipfile.ZipFile(os.path.join(self.file_path, self.historical_source.split("/")[-1]), "r") as zip_ref:
                zip_ref.extractall(self.file_path)
        except Exception as e:
            logger.error(f"Failed when trying to unzip the EMS data file. Error {e}", exc_info=True)
            raise IOError(f"Failed when trying to unzip the EMS data file. Error {e}")

        logger.info(f"Finished Unzipping EMS data")

    def download_station_data_from_databc(self):
        """
        Method that downloads the EMS Station data from DataBC using the bcdata package. It takes the databc_layer_name attribute of the class and uses it to download the corresponding data from DataBC. If the databc_layer_name is not set, it will raise an error.
        The data is downloaded in GeoPandas format, which is converted to a polars_st GeoLazyFrame. The column names are converted to
        be lowercase since they are all uppercase by default.
        If there is no data returned from DataBC, it will retry up to MAX_NUM_RETRY times.

        Args:
            None

        Output:
            None
        """
        logger.info("Using bcdata to download data from DataBC for EMS Stations")

        try:
            station_data = (
                st.from_geopandas(bcdata.get_data(self.databc_layer_name, as_gdf=True, sortby="monitoring_location_id"))
                .lazy()
                .rename(str.lower)
            )
        except Exception as e:
            logger.error(f"Failed trying to download data from DataBC using bcdata for EMS Stations. Error {e}", exc_info=True)
            raise RuntimeError(f"Failed trying to download data from DataBC using bcdata for EMS Stations. Error {e}")

        self._EtlPipeline__downloaded_data["ems_stations"] = station_data

        logger.info("Finished getting EMS station data from DataBC")

    def transform_data(self):

        logger.info(f"Starting trasformation step for {self.name}")

        try:
            downloaded_data = self.get_downloaded_data()
            historical = pl.scan_csv(self.csv_path, has_header=True, infer_schema=True, infer_schema_length=1000000)
        except Exception as e:
            logger.error(f"Failed to get downloaded data or opening CSV. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get downloaded data or opening CSV. Error: {e}")

        logger.info("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
        try:
            pl.concat([
                    downloaded_data["current"].select(QUARTERLY_EMS_COLS_TO_KEEP),
                    historical.select(QUARTERLY_EMS_COLS_TO_KEEP)
            ]).sink_csv(path = self.file_path + "combined.csv", include_header=True, float_scientific=False)
        except Exception as e:
            logger.error(f"Failed to write to CSV. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to write to CSV. Error: {e}")

        try:
            # This pl.read_csv_batched() method is a bit weird. Despite the batch size being set, it doesn't return the batch_size number of
            # rows. In addition, each batch is returned as a separate polars DataFrame.
            batch_reader = pl.read_csv_batched(
                source=self.file_path + "combined.csv",
                has_header=True,
                batch_size=100000,
                infer_schema_length=0,
                raise_if_empty=False
            )
            batch = batch_reader.next_batches(12)
        except Exception as e:
            logger.error(f"Failed to set up batch CSV reader, Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to set up batch CSV reader, Error: {e}")

        while batch:
            batch = pl.concat(batch).lazy()

            try:

                processed_data = (
                    batch
                    .rename(str.lower)
                    # Remove any empty strings, which are Null values in this case
                    .remove(
                        (pl.col("ems_id") == pl.lit("")) &
                        (pl.col("qa_index_code").is_in(["", "F"])) &
                        (pl.col("parameter") == pl.lit("")) &
                        (pl.col("result").is_null()) &
                        (pl.col("collection_start").is_null()) &
                        (pl.col("sample_class") != pl.lit("Regular")) &
                        (~pl.col("sample_state").is_in(["Fresh Water", "Fresh Water Sediment", "Ground Water", "Waste Water"]))
                    )
                    .drop("sample_class")
                    # Just incase there are string values that represents a integer in float form. The original_ids in the database use
                    # integers for the naming so it is important that any 0s after the decimal are removed.
                    .with_columns(
                        lower_depth = pl.col("lower_depth").cast(pl.String).str.replace(r"\.0\b", ""),
                        upper_depth = pl.col("upper_depth").cast(pl.String).str.replace(r"\.0\b", "")
                    )
                    .with_columns(
                        # The original scraper assumes that the timezone is in America/Vancouver and removes the daylight savings time.
                        # Trying to set the timezone in the to_datetime() function fails due to the fact that 2:00 AM doesn't exist when
                        # it goes from PST to PDT. These times that exist in UTC but not in America/Vancouver are eliminated by setting The timezone
                        # to UTC, then replacing the timezone without conversion to America/Vancouver, while setting the non-existent, and ambiguous
                        # times to NULL
                        collection_start = (
                            pl.col("collection_start")
                            .cast(pl.String)
                            .str.to_datetime("%Y%m%d%H%M%S", time_zone="UTC")
                            .dt.replace_time_zone(time_zone="America/Vancouver", non_existent="null", ambiguous="null")
                        ),
                        # This is what the original_id will be once in the database. There are depth values that are associated to the
                        # stations, and because of that, each station can multiple entry for the same day but at different depth values. That
                        # is why the depth values are appended to the network's station_ids. Some examples:
                        #
                        #   E064594 (Depth: 0 m)
                        #   E064594 (Depth: 1.5 m)
                        #   E064594 (Lower Depth: 5 m, Upper Depth: 1 m)
                        ems_id_depth = (pl
                            .when(pl.col("lower_depth").is_null() & pl.col("upper_depth").is_null())
                            .then(pl.col("ems_id"))
                            .when(pl.col("lower_depth").is_not_null() & pl.col("upper_depth").is_null())
                            .then(pl
                                .when(pl.col("lower_depth") == pl.lit("0"))
                                .then(pl.col("ems_id"))
                                .otherwise(pl.col("ems_id") + pl.lit(" (Depth: ") + pl.col("lower_depth") + pl.lit(" m)"))
                            )
                            .when(pl.col("lower_depth").is_null() & pl.col("upper_depth").is_not_null())
                            .then(pl
                                .when(pl.col("upper_depth") == pl.lit("0"))
                                .then(pl.col("ems_id"))
                                .otherwise(pl.col("ems_id") + pl.lit(" (Depth: ") + pl.col("upper_depth") + pl.lit(" m)"))
                            )
                            .when(pl.col("lower_depth") == pl.col("upper_depth"))
                            .then(pl
                                .when(pl.col("upper_depth") == pl.lit("0"))
                                .then(pl.col("ems_id"))
                                .otherwise(pl.col("ems_id") + pl.lit(" (Depth: ") + pl.col("lower_depth") + pl.lit(" m)"))
                            )
                            .when(pl.col("lower_depth").is_not_null() & pl.col("upper_depth").is_not_null())
                            .then(pl.col("ems_id") + pl.lit(" (Lower Depth: ") + pl.col("lower_depth") + pl.lit(" m, Upper Depth: ") + pl.col("upper_depth") + pl.lit(" m)"))
                            .otherwise(pl.lit(None))
                        ),
                        unit = pl.col("unit").str.replace(",", ""),
                        result_text = (pl
                            .when((pl.col("result_letter").is_null()) | (pl.col("result_letter") == pl.lit("M")))
                            .then(pl.col("result"))
                            .otherwise(pl.col("result_letter") + pl.col("result").cast(pl.String))
                        ),
                        parameter_code_units = pl.lit(None).cast(pl.String)
                    )
                    .drop(
                        "lower_depth",
                        "upper_depth"
                    )
                    .unique(keep="last")
                )
            except Exception as e:
                logger.error(f"Failed initial data processing (Pre new station insert). Please check and fix. Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed initial data processing (Pre new station insert). Please check and fix. Error: {e}")

            logger.info(f"Getting all EMS location type codes from database")

            try:
                location_type_codes = pl.read_database(query="SELECT location_type_code, include FROM bcwat_obs.water_quality_ems_location_type;", connection=self.db_conn).lazy()
            except Exception as e:
                logger.error(f"Failed when trying to get EMS location type codes from database. Error {e}", exc_info=True)
                raise RuntimeError(f"Failed when trying to get EMS location type codes from database. Error {e}")

            logger.info("Checking if there are any new EMS location type codes that needs to be inserted into the database.")

            try:
                new_station_codes = (
                    downloaded_data["ems_stations"]
                    .rename({"location_type_cd": "location_type_code"})
                    .join(
                        other=location_type_codes,
                        on="location_type_code",
                        how="anti"
                    )
                ).collect()

                if not new_station_codes.is_empty():
                    logger.warning(NEW_EMS_LOCATION_TYPE_CODE_MESSAGE)

                    self.__insert_metadata(new_station_codes, "new_station_codes", ["location_type_code"])
                else:
                    logger.info(f"No new location type codes found. Moving on")
            except Exception as e:
                logger.error(f"Failed checkinng for new location type codes. Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed checkinng for new location type codes. Error: {e}")

            try:
                logger.info("Getting and inserting new stations.")

                stations_to_scrape = self.get_and_insert_new_stations(processed_data)
            except Exception as e:
                logger.error(f"Failed to collect and insert new stations in to the database. Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed to collect and insert new stations in to the database. Error: {e}")

            try:
                logger.info("Checking if there are new units")

                all_units = self.__get_and_insert_new_units(processed_data)
            except Exception as e:
                logger.error(f"Failed trying to get and insert new units. Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed trying to get and insert new units. Error: {e}")

            try:
                logger.info("Checking if there are new parameters in the data")

                all_params = self.__get_and_insert_new_params(processed_data)
            except Exception as e:
                logger.error(f"Failed trying to get and insert new parameters. Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed trying to get and insert new parameters. Error: {e}")

            self.get_all_stations_in_network()

            try:
                processed_data = (
                    processed_data
                    .rename({"parameter": "parameter_name", "unit": "unit_name"})
                    .join(
                        other=all_units,
                        on="unit_name",
                        how="inner"
                    )
                    .join(
                        other=all_params,
                        on="parameter_name",
                        how="inner"
                    )
                    .join(
                        other=stations_to_scrape.select("ems_id_depth"),
                        on="ems_id_depth",
                        how="inner"
                    )
                    .rename({"ems_id_depth": "original_id"})
                    .join(
                        other = self.all_stations_in_network,
                        on="original_id",
                        how="inner"
                    )
                    .filter(
                        pl.col("result").is_not_null() &
                        pl.col("station_id").is_not_null() &
                        pl.col("collection_start").is_not_null() &
                        pl.col("parameter_id").is_not_null() &
                        pl.col("unit_id").is_not_null()
                    )
                    .with_columns(
                        qa_id = pl.lit(1),
                        result_letter = (pl
                            .when(pl.col("result_letter") == pl.lit("M"))
                            .then(None)
                            .otherwise(pl.col("result_letter"))
                        )
                    )
                    .select(
                        pl.col("station_id"),
                        pl.col("collection_start").alias("datetimestamp"),
                        pl.col("parameter_id"),
                        pl.col("unit_id"),
                        pl.col("qa_id"),
                        pl.col("location_purpose"),
                        pl.col("sampling_agency"),
                        pl.col("analyzing_agency"),
                        pl.col("collection_method"),
                        pl.col("sample_state"),
                        pl.col("sample_descriptor"),
                        pl.col("analytical_method"),
                        pl.col("qa_index_code"),
                        pl.col("result").alias("value"),
                        pl.col("result_text").alias("value_text"),
                        pl.col("result_letter").alias("value_letter")
                    )
                    .sort(by=["station_id", "datetimestamp", "parameter_id", "unit_id", "value_text"], descending=True)
                    .unique(subset=["station_id", "datetimestamp", "parameter_id", "unit_id"], keep="first")
                )
            except Exception as e:
                logger.error(f"Failed to transform second round of transformations, after the new stations insert. Error {e}", exc_info=True)
                raise RuntimeError(f"Failed to transform second round of transformations, after the new stations insert. Error {e}")

            try:
                self._EtlPipeline__transformed_data = {
                    "df": processed_data,
                    "pkey": ["station_id", "datetimestamp", "parameter_id", "unit_id"],
                }

                self.load_data()
            except Exception as e:
                logger.error(f"Failed to load transformed data into the database. Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed to load transformed data into the database. Error: {e}")

            batch = batch_reader.next_batches(12)

        self.db_conn.commit()

        logger.info(f"Finished transformation and loading data into the database for {self.name}")


    def get_and_insert_new_stations(self, processed_data):
        """
        Method that checks if there are new stations in the EMS Station data from DataBC. If there are new stations, it inserts them into the database along with their metadata.

        Args:
            processed_data (pl.LazyFrame): LazyFrame that has been processed and transformed from the EMS Station data from DataBC.

        Output:
            pl.LazyFrame: LazyFrame of the EMS Stations to be scraped for data from DataBC after the new stations have been inserted into the database.
        """
        logger.info(f"Checking if there are new stations in the EMS Station data from DataBC")

        self.get_all_stations_in_network()
        location_type_codes = pl.read_database(query="SELECT location_type_code, location_type_description FROM bcwat_obs.water_quality_ems_location_type WHERE include;", connection=self.db_conn).lazy()

        try:
            stations_to_scrape = (
                processed_data
                .select(
                    "ems_id",
                    "ems_id_depth",
                    "location_purpose"
                )
                .unique(subset=["ems_id", "ems_id_depth"])
                .join(
                other=self.get_downloaded_data()["ems_stations"].rename({"monitoring_location_id":"ems_id", "location_type_cd": "location_type_code"}),
                on="ems_id",
                how="left"
                )
                .join(
                other=location_type_codes,
                on="location_type_code",
                how="inner"
                )
                .unique(subset="ems_id_depth")
            )
        except Exception as e:
            logger.error("Failed to check if there were new stations in the EMS Station data from DataBC. Please check what the error was and rerun. Error {e}", exc_info=True)
            raise RuntimeError("Failed to check if there were new stations in the EMS Station data from DataBC. Please check what the error was and rerun. Error {e}")

        try:
            new_stations = (
                stations_to_scrape
                .rename({"ems_id_depth": "original_id"})
                .join(
                    other = self.all_stations_in_network,
                    on="original_id",
                    how="anti"
                )
            ).collect()
        except Exception as e:
            logger.error(f"Failed to get the list of new stations in the data. Raising error since it cannot keep scraping without removing potential new stations. Error: {e}", exc_info=True)
            raise RuntimeError("Failed to get the list of new stations in the data. Raising error since it cannot keep scraping without removing potential new stations. Error: {e}")

        if new_stations.is_empty():
            logger.info("Found no new stations in the EMS Station data from DataBC")
            return stations_to_scrape

        try:
            rename_dict = (
                new_stations
                .with_columns(
                    regex_onestring = pl.col("monitoring_location_name").str.to_titlecase().str.extract(r"([A-Z]{1}[a-z]{1}[0-9]+)", 1),
                    regex_hiphen = pl.col("monitoring_location_name").str.to_titlecase().str.extract(r"([A-Z]{1}[a-z]{1}-[0-9]+)", 1),
                    regex_space = pl.col("monitoring_location_name").str.to_titlecase().str.extract(r"([A-Z]{1}[a-z]{1,2}\x20[0-9]+)", 1),
                )
                .select(
                    "regex_onestring",
                    "regex_hiphen",
                    "regex_space"
                )
            )
        except Exception as e:
            logger.error(f"Failed to create the rename_dict DataFrame with the strings that needs to be replaced in the monitoring_location_name column. Please check why it failed and rerun. Error{e}", exc_info=True)
            raise RuntimeError(f"Failed to create the rename_dict DataFrame with the strings that needs to be replaced in the monitoring_location_name column. Please check why it failed and rerun. Error{e}")

        try:
            new_ems_stations = (
                new_stations.lazy()
                .with_columns(
                    network_id = 25,
                    station_name = (pl
                        .when(pl.col("monitoring_location_name").is_not_null())
                        .then(
                            (pl
                            .col("monitoring_location_name")
                            .str.to_titlecase()
                            .str.replace_many(STATION_NAME_LOWER_TO_UPPER_CASE_DICT)
                            .str.replace_many(
                                dict(rename_dict
                                .with_columns(
                                    upper = (
                                        pl.col("regex_onestring")
                                        .str.to_uppercase()
                                    )
                                )
                                .select("regex_onestring","upper")
                                .filter(pl.col("upper").is_not_null())
                                .iter_rows()
                                )
                            )
                            .str.replace_many(
                                dict(rename_dict
                                .with_columns(
                                    upper = (
                                        pl.col("regex_hiphen")
                                        .str.to_uppercase()
                                    )
                                )
                                .select("regex_hiphen","upper")
                                .filter(pl.col("upper").is_not_null())
                                .iter_rows()
                                )
                            )
                            .str.replace_many(
                                dict(rename_dict
                                .with_columns(
                                    upper = (
                                        pl.col("regex_space")
                                        .str.to_uppercase()
                                    )
                                )
                                .select("regex_space","upper")
                                .filter(pl.col("upper").is_not_null())
                                .iter_rows()
                                )
                            )
                            )
                        )
                        .otherwise(pl.col("ems_id"))
                    ),
                    # Make sure that longitude is negative
                    longitude = pl.col("longitude").abs() * -1,
                    type_id = (pl
                        .when(pl.col("location_type_code").is_in(["D4", "D7", "D3", "38", "33", "45"]))
                        .then(5)
                        .otherwise(4)
                    ),
                    station_status_id = pl.lit(None).cast(pl.Int8),
                    operation_id = pl.lit(None).cast(pl.Int8),
                    drainage_area = pl.lit(None).cast(pl.Float32),
                    scrape = False,
                    regulated = False,
                    user_flag = False,
                    stream_name = pl.lit(None).cast(pl.String),
                    station_description = pl.lit(None).cast(pl.String),
                    year = pl.lit([self.date_now.year]).cast(pl.List(pl.Int32)),
                    project_id = pl.lit([6]),
                    variable_id = pl.lit([1])
                )
                .select(
                    pl.col("original_id"),
                    pl.col("station_name"),
                    pl.col("station_status_id"),
                    pl.col("longitude"),
                    pl.col("latitude"),
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
                    pl.col("variable_id"),
                )
            )
        except Exception as e:
            logger.error(f"Failed to construct the DataFrame that will be going into the `construct_insert_tables()` function to create the correct metadata DataFrames for each station. Error {e}", exc_info=True)
            raise RuntimeError(f"Failed to construct the DataFrame that will be going into the `construct_insert_tables()` function to create the correct metadata DataFrames for each station. Error {e}")

        logger.info(f"Constructing insert tables for new stations")

        try:
            new_ems_stations, insert_dict = self.construct_insert_tables(new_ems_stations)
        except Exception as e:
            logger.error(f"Failed to construct the DataFrames to insert into the database. Error: {e}")
            raise RuntimeError(f"Failed to construct the DataFrames to insert into the database. Error: {e}")


        logger.info(f"Inserting new stations for {self.name} into the database")

        try:
            self.insert_new_stations(new_ems_stations, insert_dict)
        except Exception as e:
            logger.error(f"Failed to insert new stations in to the database. Error: {e}")
            raise RuntimeError(f"Failed to insert new stations in to the database. Error: {e}")

        return stations_to_scrape

    def __get_and_insert_new_units(self, processed_data):
        """
        Identifies new water quality units from the processed data and inserts them into the database
        if they do not already exist. Returns an updated list of all units in the database.

        Args:
            processed_data (polars.LazyFrame): The processed data containing unit information from
            which new units will be identified and inserted.

        Returns:
            polars.LazyFrame: A LazyFrame containing all water quality units currently in the database,
            including any newly inserted units.
        """

        try:
            units_in_db = pl.read_database(query="SELECT unit_id, unit_name from bcwat_obs.water_quality_unit;", connection=self.db_conn).lazy()
        except Exception as e:
            logger.error(f"Failed to get water quality units already in the database, please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get water quality units already in the database, please fix and rerun. Error: {e}")

        try:
            new_units = (
                processed_data
                .select(
                    pl.col("unit").alias("unit_name")
                )
                .filter(pl.col("unit_name").is_not_null())
                .unique()
                .join(
                    other=units_in_db,
                    on="unit_name",
                    how="anti"
                )
            ).collect()
        except Exception as e:
            logger.error(f"Failed to find new units by comparing the units in the data against the units in the database. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to find new units by comparing the units in the data against the units in the database. Error: {e}")

        if new_units.is_empty():
            logger.info("There are no new units in the data. Moving on")
            return units_in_db

        try:
            logger.info(f"Found new units in the data, inserting them into the database:\n{", ".join(new_units["unit_name"].to_list())}")
            self.__insert_metadata(data=new_units, tablename="new_units", pkey=["unit_id"])
        except Exception as e:
            logger.error(f"Failed to insert new units in to the database. Please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to insert new units in to the database. Please fix and rerun. Error: {e}")

        logger.info("Getting all units in database, including the new ones")
        try:
            units_in_db = pl.read_database(query="SELECT unit_id, unit_name from bcwat_obs.water_quality_unit;", connection=self.db_conn).lazy()
        except Exception as e:
            logger.error(f"Failed to get water quality units in the database, please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get water quality units in the database, please fix and rerun. Error: {e}")

        return units_in_db

    def __get_and_insert_new_params(self, processed_data):
        """
        Method that checks if there are new parameters in the EMS data from DataBC. If there are new parameters, a chemistry NLP is spun up to determine the grouping of the new parameters. After this is complete for each new parameter it inserts them into the database.

        Args:
            processed_data (pl.LazyFrame): LazyFrame that has been processed and transformed from the EMS Station data from DataBC.

        Output:
            pl.LazyFrame: LazyFrame of the water quality parameters to be scraped for data from DataBC after the new parameters have been inserted into the database.
        """
        try:
            parameters_in_db = pl.read_database(query="SELECT parameter_id, parameter_name from bcwat_obs.water_quality_parameter;", connection=self.db_conn).lazy()
        except Exception as e:
            logger.error(f"Failed to get water quality parameters already in the database, please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get water quality parameters already in the database, please fix and rerun. Error: {e}")

        try:
            new_parameters = (
                processed_data
                .select(
                    pl.col("parameter").alias("parameter_name")
                )
                .unique()
                .filter(pl.col("parameter_name").is_not_null())
                .join(
                    other=parameters_in_db,
                    on="parameter_name",
                    how="anti"
                )
            ).collect()
        except Exception as e:
            logger.error(f"Failed to find new parameters by comparing the parameters in the data against the parameters in the database. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to find new parameters by comparing the parameters in the data against the parameters in the database. Error: {e}")

        if new_parameters.is_empty():
            logger.info("There are no new parameters in the data. Moving on")
            return parameters_in_db

        logger.info("New parameters found. Spinning up NLP to determine the groupings.")

        # Add the new columns that is needed
        new_parameters = (
            new_parameters
            .with_columns(
                grouping_name = pl.lit(None).cast(pl.String),
            )
        )

        try:

            chemist = NLP(self.db_conn)
            chemist.run()

            for row in new_parameters.rows():
                category, percentage = chemist.predict(row[0])
                new_parameters = (
                    new_parameters
                    .with_columns(
                        grouping_name = (pl
                            .when(pl.col("parameter_name") == pl.lit(row[0]))
                            .then(pl.lit(category))
                            .otherwise(pl.col("grouping_name"))
                        )
                    )
                )
        except Exception as e:
            logger.error(f"Failed to run the Chemist NLP to group the parameters in to the correct grouping id. Please check and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to run the Chemist NLP to group the parameters in to the correct grouping id. Please check and rerun. Error: {e}")

        try:
            parameter_groupings = pl.read_database(query="SELECT grouping_id, grouping_name FROM bcwat_obs.water_quality_parameter_grouping;", connection = self.db_conn)

            new_parameters = (
                new_parameters
                .join(
                    other=parameter_groupings,
                    on="grouping_name",
                    how="inner"
                )
                .with_columns(
                    parameter_desc = pl.col("parameter_name").str.replace(r"total|dissolved|reactive|extractable|extractble|extractbl", "")
                )
                .select(
                    "parameter_name",
                    "parameter_desc",
                    "grouping_id"
                )
            )
        except Exception as e:
            logger.error(f"Failed to get the grouping_id of each grouping, joining the new_parameters to the correct grouping_ids. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get the grouping_id of each grouping, joining the new_parameters to the correct grouping_ids. Error: {e}")

        try:
            logger.info(f"Found new parameters in the data, inserting them into the database:\n{", ".join(new_parameters["parameter_name"].to_list())}")
            self.__insert_metadata(data=new_parameters, tablename="new_parameters", pkey=["parameter_id"])
        except Exception as e:
            logger.error(f"Failed to insert new parameters in to the database. Please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to insert new parameters in to the database. Please fix and rerun. Error: {e}")

        logger.info("Getting all parameters in the database, including the ones that were just inserted.")
        try:
            parameters_in_db = pl.read_database(query="SELECT parameter_id, parameter_name from bcwat_obs.water_quality_parameter;", connection=self.db_conn).lazy()
        except Exception as e:
            logger.error(f"Failed to get water quality parameters in the database, please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get water quality parameters in the database, please fix and rerun. Error: {e}")

        return parameters_in_db


    def load_data(self):
        """
        load_data from StationObservationPipeline has been overwritten to be this function. This was required because there are significantly more columns being inserted to the database, and there are more columns that need to be updated in the case of a duplicate.

        Args:
            None

        Output:
            None
        """
        logger.info("Loading water quality data into the table bcat_obs.water_quality_hourly.")
        try:
            insert_data = self.get_transformed_data()
            data = insert_data["df"].collect()

            cols = data.columns

            query = f"""
                INSERT INTO
                    bcwat_obs.water_quality_hourly({", ".join(cols)})
                VALUES %s
                ON CONFLICT
                    ({", ".join(insert_data["pkey"])})
                DO UPDATE SET
                    qa_id = EXCLUDED.qa_id,
                    location_purpose = EXCLUDED.location_purpose,
                    sampling_agency = EXCLUDED.sampling_agency,
                    analyzing_agency = EXCLUDED.analyzing_agency,
                    collection_method = EXCLUDED.collection_method,
                    sample_state = EXCLUDED.sample_state,
                    sample_descriptor = EXCLUDED.sample_descriptor,
                    analytical_method = EXCLUDED.analytical_method,
                    qa_index_code = EXCLUDED.qa_index_code,
                    value = EXCLUDED.value,
                    value_text = EXCLUDED.value_text,
                    value_letter = EXCLUDED.value_letter;
            """

            cursor = self.db_conn.cursor()

            execute_values(cur=cursor, sql=query, argslist=data.rows(), page_size=100000)
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Failed to insert EMS data in to the database. Please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to insert EMS data in to the database. Please fix and rerun. Error: {e}")

        logger.info("Finished loading data fro this batch. Collecting more batches to see if there are anymore data")

    def __insert_metadata(self, data, tablename, pkey):
        """
        Inserts metadata into the specified database table. If a conflict arises with existing data based on the
        primary key, it does nothing when duplicate entries have been attempted to be inserted.

        Args:
            data (polars.DataFrame): The data to be inserted into the database table.
            tablename (str): The name of the table into which data will be inserted.
            pkey (list): A list of column names that are considered as the primary keys for identifying conflicts.

        Output:
            None
        """

        try:
            cursor = self.db_conn.cursor()
            rows = data.rows()
            cols = data.columns
            query = f"INSERT INTO {self.destination_tables[tablename]}({', '.join(cols)}) VALUES %s ON CONFLICT ({', '.join(pkey)}) DO NOTHING;"
            execute_values(cur=cursor, sql=query, argslist=rows, page_size=100000)
            self.db_conn.commit()
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Failed to insert EMS {tablename} data in to the database. Please fix and rerun. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to insert EMS {tablename} data in to the database. Please fix and rerun. Error: {e}")
