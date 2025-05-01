from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import(
    FLOWWORKS_NAME,
    FLOWWORKS_DESTINATION_TABLE,
    FLOWWORKS_RENAME_DICT,
    FLOWWORKS_BASE_URL,
    FLOWWORKS_TOKEN_URL,
    FLOWWORKS_DTYPE_SCHEMA,
    FLOWWORKS_IDEAL_VARIABLES,
    HEADER,
    FAIL_RATIO,
    SPRING_DAYLIGHT_SAVINGS
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl
import pendulum
import requests
import json

## This is temporary until I can talk to Liam about secrets
import os


logger = setup_logging()

class FlowWorksPipeline(StationObservationPipeline):
    def __init__(self, db_conn = None, date_now = None, station_source = 'crd_flowworks'):
        super().__init__(name=FLOWWORKS_NAME, source_url=[], destination_tables=FLOWWORKS_DESTINATION_TABLE)

        self.days = 2
        self.station_source = station_source
        self.expected_dtype = FLOWWORKS_DTYPE_SCHEMA
        self.column_rename_dict = FLOWWORKS_RENAME_DICT
        self.go_through_all_stations = False
        self.variable_to_scrape  = {}

        self.db_conn = db_conn
        self.date_now = date_now.in_tz("America/Vancouver")
        self.bearer_token = None

        self.__get_flowworks_token()
        self.get_station_list()

        # The stations have all been prepended with a "HRB" prefix, but the ids in flowwork doesn not have "HRB", so remove them.
        self.station_list = (
            self.station_list
            .with_columns(
                original_id = pl.col("original_id").str.slice(3)
            )
        )

        # This scraper has two similar sources but scrapes different information.
        self.source_url = FLOWWORKS_BASE_URL

    def download_data(self):
        """
        Custom data download function since this uses an API instead of a download URL. Otherwise the idea is the same, Load to polars dataframe
        and assign it to _EtlPipeline__downloaded_data in a dictionary

        Args:
            None

        Output:
            None
        """
        headers = HEADER
        headers["Authorization"] = f"Bearer {self.bearer_token}"

        logger.debug("Getting all station metadata from the FlowWorks API")

        station_data = self.__get_flowworks_station_data(headers)

        failed_downloads = 0
        for station_info in station_data.collect().iter_rows():

            logger.info(f"Downloading data for station {station_info[0]}")
            self._EtlPipeline__download_num_retries = 0
            while True:
                # Try to get station variable data from API
                url = f"{self.source_url}{station_info[0]}/channels"
                data_request = requests.get(url, headers=headers)

                # Check if the request response is 200
                if (data_request.status_code != 200) and (self._EtlPipeline__download_num_retries < 3):
                    logger.warning(f"Failed to download data from {url}, status code was not 200! Status: {data_request.status_code}, Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    continue
                elif (data_request.status_code != 200) and (self._EtlPipeline__download_num_retries == 3):
                    break

                # Checking for any issues within API 
                try:
                    self.__check_api_request_response(data_request.json())
                except (RuntimeError, KeyError) as e:
                    if self._EtlPipeline__download_num_retries < 3:
                        self._EtlPipeline__download_num_retries += 1
                        continue
                    else:
                        logger.error(f"Got a 200 status code response from the API but failed the check for errors. Error: {e}")
                        data_request = None
                        break
                
                # Since there are variables that represent data type but with different variable names, they must be ranked in
                # order of preference.
                try:
                    self.__find_ideal_variables(data_request.json()["Resources"])
                except KeyError as e:
                    logger.error(f"Failed to find ideal variables, there may have been a key mismatch. Error: {e}")
                    data_request = None
                    break

                logger.debug(f"Getting data from API for each variable that found it's best match")
                try:
                    var_with_no_data_count = 0
                    for key in self.variable_to_scrape.keys():

                        # If there were no variables that match, then make dict entry `None`and continue to next variable
                        if self.variable_to_scrape[key] is None:
                            # There are cases where the stations that we are scraping have no data to report. In those cases, move on gracefully.
                            var_with_no_data_count += 1
                            if var_with_no_data_count == len(self.variable_to_scrape.keys()):
                                logger.warning(f"There was no data to be scraped for any variables for station ID {station_info[0]}. Moving on to next station. Not marking as a failed scrape.")
                            continue

                        data_url = f"{url}/{self.variable_to_scrape[key]}/data?intervalTypeFilter=D&intervalNumberFilter={self.days}"
                        data_request = requests.get(data_url, headers=headers)

                        # Check if the request response is 200
                        if data_request.status_code != 200:
                            raise RuntimeError(f"Failed to download data from {data_url}, status code was not 200! Status: {data_request.status_code}. Retrying")
                        
                        # Check if the requested data has any viable data
                        if not data_request.json()["Resources"]:
                            logger.warning(f"Did not find any data in the response for {key}. But the request was successful so not marking as failure. Be noted")
                            continue
                        
                        requested_data = (
                            pl.LazyFrame(data_request.json()["Resources"], schema_overrides=self.expected_dtype[key])
                            .with_columns(original_id = station_info[0])
                        )

                        if key not in self._EtlPipeline__downloaded_data.keys():
                            self._EtlPipeline__downloaded_data[key] = requested_data
                        else:
                            self._EtlPipeline__downloaded_data[key] = pl.concat([self._EtlPipeline__downloaded_data[key], requested_data])
                    
                    # If we get here, that means that all data that can be collected has been collected successfully and we can break out of the retry loop.
                    break
                            
                except RuntimeError as e:
                    if self._EtlPipeline__download_num_retries < 3:
                        logger.warning(str(e))
                        self._EtlPipeline__download_num_retries += 1
                        continue
                    else:
                        logger.error(f"Got 200 response from API but failed to check for errors. Error: {e}")
                        data_request = None
                        break
                except Exception as e:
                    logger.error(f"An error occurred while trying to download data from {data_url} for station_id {station_info[0]}, Error: {e}. Marking as failed to download and continuing on to next station")
                    data_request = None
                    break
            
            if data_request is None:
                failed_downloads += 1
                continue


        if failed_downloads/(self.station_list.collect().shape[0]) > FAIL_RATIO:
            logger.error(f"More than 50% of the data was not downloaded, exiting")
            raise RuntimeError(f"More than 50% of the data was not downloaded. {failed_downloads} out of {len(self.source_url.keys())} failed to download. for {self.name} pipeline")
        
        logger.info(f"Finished downloading data for {self.name}")

    


    def transform_data(self):
        """
        Custom transformation function for the FlowWorks pipeline. Goes through each key in the __downloaded_data attribute and applies the transformations.

        Args:
            None

        Output:
            None
        """

        logger.info("Starting transformation for FlowWorks pipeline")

        downloaded_data = self.get_downloaded_data()

        # Check to see if the downloaded data actually exists
        if not downloaded_data:
            if self.station_source == "flowworks":
                logger.warning("No data was downloaded to be transformed for the FlowWorks pipeline. This is expected. Exiting pipeline")
                return
            else:
                logger.error("No data was downloaded to be transformed for the CRD FlowWorks pipeline. This is not expected since it is the CRD FlowWorks Pipeline.")

        for key in downloaded_data.keys():
            df = downloaded_data[key]
            try:
                # General Transformations
                # Tried to do the .with_columns(datestamp) transformation in one .with_columns block but it failed. splitting it up seems to 
                # work fine.
                df = (
                    df
                    .rename(self.column_rename_dict)
                    .remove(datestamp = pl.col("datestamp").str.replace("T", " ").str.slice(offset=0, length=14).str.pad_end(16, "0").is_in(SPRING_DAYLIGHT_SAVINGS))
                    .with_columns(datestamp = pl.col("datestamp").str.to_datetime("%Y-%m-%dT%H:%M:%S", time_zone = "America/Vancouver", ambiguous="earliest"))
                    .with_columns(
                        qa_id = pl.when(key in ["temperature", "swe", "rainfall", "pc"])
                            .then(1)
                            .otherwise(0),
                        variable_id = pl.when(key == "discharge")
                            .then(1)
                            .when(key == "stage")
                            .then(2)
                            .when(key == "pc")
                            .then(28)
                            .when(key == "rainfall")
                            .then(29)
                            .when(key == "temperature")
                            .then(7)
                            .when(key == "swe")
                            .then(16),
                        datestamp = pl.col("datestamp").dt.date()
                    )
                    .remove((pl.col("value") == 999999) | (pl.col("value").is_null()) | (pl.col("value").is_nan()))
                    .remove((pl.col("variable_id") == 16) & (pl.col("value") < 0))
                    .join(self.station_list.with_columns(original_id = pl.col("original_id").cast(pl.Int32)), on="original_id", how="inner")
                )
                
                # Variable specific transformations 
                if key in ["discharge", "stage"]:
                    df = (
                        df
                        .group_by(["station_id", "datestamp"]).agg([pl.mean("value"), pl.min("qa_id"), pl.min("variable_id")])
                        .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
                    ).collect()
                    
                    self._EtlPipeline__transformed_data[key] = [df, ["station_id", "datestamp"]]
                elif key in ["swe", "rainfall", "pc"]:
                    df = (
                        df
                        .group_by(["station_id", "datestamp"]).agg([pl.sum("value"), pl.min("qa_id"), pl.min("variable_id")])
                        .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
                    ).collect()
                    
                    self._EtlPipeline__transformed_data[key] = [df, ["station_id", "datestamp"]]
                elif key == "temperature":
                    df_min = (
                        df
                        .group_by(["station_id", "datestamp"]).agg([pl.min("value"), pl.min("qa_id"), pl.min("variable_id")])
                        .with_columns(variable_id = 8)
                        .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
                    )
                    df_max = (
                        df
                        .group_by(["station_id", "datestamp"]).agg([pl.min("value"), pl.min("qa_id"), pl.min("variable_id")])
                        .with_columns(variable_id = 6)
                        .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
                    )
                    df_avg = (
                        df
                        .group_by(["station_id", "datestamp"]).agg([pl.mean("value"), pl.min("qa_id"), pl.min("variable_id")])
                        .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
                    )

                    df = pl.concat([df_min, df_avg, df_max]).collect()
                    self._EtlPipeline__transformed_data[key] = [df, ["station_id", "datestamp", "variable_id"]]

            except Exception as e:
                logger.error(f"There was an error when trying to transform the data for {key}. Error: {e}")


    def validate_downloaded_data(self):
        """
        Basically the same function as the base class. The only difference is that the "original_id" column gets added after the schema is overriden.

        Args:
            None

        Output:
            None
        """
        # Since the "original_id" column gets added after the schema is overriden, it does not exist in the expected_dtype dict.
        # So add it in

        if not self._EtlPipeline__downloaded_data:
            if self.station_source == "flowworks":
                logger.warning("No data was downloaded to be validated for the FlowWorks pipeline. This is expected. Exiting pipeline")
                return
            else:
                logger.error("No data was downloaded to be validated for the CRD FlowWorks pipeline. This is not expected since it is the CRD FlowWorks Pipeline.")

        for key in self.expected_dtype.keys():
            self.expected_dtype[key]["original_id"] = pl.Int32
        
        # Call the original validation function
        super().validate_downloaded_data()

    def load_data(self):
        """
        There is a chance that FlowWorks has no data, this is expected and needs to be handled. The beginning of this function is changed a little to ensure that the empty cases are handled correctly. Otherwise it is the same function as the one in EtlPipeline.

        Args:
            None
        
        Output:
            None
        """

        if not self._EtlPipeline__transformed_data:
            if self.station_source == "flowworks":
                logger.warning("No data was downloaded to be loaded on to the database for the FlowWorks pipeline. This is expected. Exiting pipeline")
                return
            else:
                logger.error("No data was downloaded to be loaded on to the database for the CRD FlowWorks pipeline. This is not expected since it is the CRD FlowWorks Pipeline.")
                raise ValueError(f"No data exists in the _EtlPipeline__transformed_data attribute! Expected at least a little.")

        super().load_data()

    def __get_flowworks_token(self):
        """
        FlowWorks API requires a bearer token to be used. This function will get that token.

        Args:
            None

        Output:
            None
        """

        # Not sure if I should store these in the class attributes. Feels a bit dangerous.
        flowworks_credentials = {
            "UserName": os.getenv("FLOWWORKS_USER"),
            "Password": os.getenv("FLOWWORKS_PASS"),
        }
        
        headers = HEADER
        headers["Content-type"] = "application/json"
        
        token_post = requests.post(FLOWWORKS_TOKEN_URL, headers=headers, data=json.dumps(flowworks_credentials))
        
        self.bearer_token =  token_post.json()

    def __get_flowworks_station_data(self, headers):
        """
        FlowWorks requires us to work with their API, this is the function that will grab the station metadata and return it as a polars dataframe. This will not be needed to be done like
        this if we do not need to add any new stations. This will be discussed with Ben soon.

        Args:
            None

        Output:
            station_data (pl.LazyFrame): Polars LazyFrame object with Station metadata for stations that have been filtered by those in the database.
        """
        logger.info(f"Getting station data from the FlowWorks API")

        response = requests.get(self.source_url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Failed to download data from {self.source_url}, status code was not 200! Status: {response.status_code}")
            raise RuntimeError(f"Failed to download data from {self.source_url}, status code was not 200! Status: {response.status_code}")

        data_json = response.json()
        
        # Check if the request results are as expected
        try:
            self.__check_api_request_response(data_json)
        except (RuntimeError, KeyError) as e:
            #Send Email Here
            raise RuntimeError(e)
        
        # Load station data in to LazyFrame
        # TODO: Implement method to add new stations that were found in the response and does not exist in the db.

        station_data = (
            pl.LazyFrame(data_json["Resources"])
            .with_context(self.station_list)
            .filter(pl.col("Id").is_in(pl.col("original_id").cast(pl.Int64)))
        )

        return station_data
    
    def __check_api_request_response(self, response):
        """
        Verification function that checks if the contents of the API requests are as expected. If not it will raise an error
        that should be caught in the function that called it.

        Args:
            response (dict): The response from the API.

        Output:
            None
        """
        # Check if the request results are as expected
        try:
            if response["ResultCode"] != 0:
                logger.error(f"Scraping for flowworks failed as the API ResultCode was not 0! ResultCode: {response['ResultCode']}")
                raise RuntimeError(f"Scraping for flowworks failed as the API ResultCode was not 0! ResultCode: {response['ResultCode']}")
            
            elif response["ResultMessage"] != "Request OK – Request is valid and was accepted.":
                logger.error(f"Scraping for flowworks failed as the API ResultMessage was not 'Request OK'! ResultMessage: {response['ResultMessage']}")
                raise RuntimeError(f"Scraping for flowworks failed as the API ResultMessage was not 'Request OK'! ResultMessage: {response['ResultMessage']}")

        except KeyError as e:
            logger.error(f"Scraping for flowworks failed as the API response did not contain the key {e}! Response: {response}")
            raise RuntimeError(f"Scraping for flowworks failed as the API response did not contain the key {e}! Response: {response}")
        
    def __find_ideal_variables(self, response_data):
        """
        FlowWorks have a large number of variables. This function will find the ideal variables to scrape from the list of all variables. The 
        ideal variables are ranked in the FLOWWORKS_IDEAL_VARIABLES dict, which is defined in the constants file.

        Args:
            response_data (json): The response from the API.

        Output:
            None
        """

        logger.info(f"Finding ideal variables from FlowWorks Channels")
        df = pl.LazyFrame(response_data)

        for key in FLOWWORKS_IDEAL_VARIABLES.keys():
            ideal_vars = FLOWWORKS_IDEAL_VARIABLES[key].copy()
            del ideal_vars["unit"]
            vars_df = pl.LazyFrame({
                "Name": ideal_vars.keys(),
                "var_rank": ideal_vars.values()
                }
            )
            filtered_df = (
                df
                .join(vars_df, on="Name", how="inner")
                .sort("var_rank")
            ).collect()

            if filtered_df.is_empty():
                self.variable_to_scrape[key] = None
            else:
                self.variable_to_scrape[key] = filtered_df["Id"][0]

