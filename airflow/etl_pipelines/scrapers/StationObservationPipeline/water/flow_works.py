from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import(
    FLOWWORKS_NAME,
    FLOWWORKS_DESTINATION_TABLE,
    FLOWWORKS_RENAME_DICT,
    FLOWWORKS_BASE_URL,
    FLOWWORKS_TOKEN_URL,
    FLOWWORKS_DTYPE_SCHEMA,
    FLOWWORKS_IDEAL_VARIABLES,
    FLOWWORKS_NETWORK,
    FLOWWORKS_STATION_SOURCE,
    HEADER,
    FAIL_RATIO,
    SPRING_DAYLIGHT_SAVINGS
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl
import requests
import json
import time
## This is temporary until I can talk to Liam about secrets
import os

logger = setup_logging()

class FlowWorksPipeline(StationObservationPipeline):
    def __init__(self, db_conn = None, date_now = None):
        super().__init__(
            name=FLOWWORKS_NAME, 
            source_url=[], 
            destination_tables=FLOWWORKS_DESTINATION_TABLE, 
            days=2, 
            station_source=FLOWWORKS_STATION_SOURCE, 
            expected_dtype=FLOWWORKS_DTYPE_SCHEMA, 
            column_rename_dict=FLOWWORKS_RENAME_DICT, 
            go_through_all_stations=True, 
            network_ids= FLOWWORKS_NETWORK,
            db_conn=db_conn
        )

        self.date_now = date_now.in_tz("America/Vancouver")
        self.variable_to_scrape  = {}
        self.auth_header = HEADER
        self.source_url = FLOWWORKS_BASE_URL
        
        self.__get_flowworks_token()
        self.get_station_list()

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
        logger.info("Getting all station metadata from the FlowWorks API")

        station_data = self.__get_flowworks_station_data()

        failed_downloads = 0
        for station_info in station_data.collect().iter_rows():

            logger.debug(f"Downloading data for station {station_info[0]}")
            self._EtlPipeline__download_num_retries = 0
            while True:
                # Try to get station variable data from API
                # Since there are variables that represent data type but with different variable names, they must be ranked in
                # order of preference.
                try:
                    url = f"{self.source_url}{station_info[0]}/channels"
                    self.__find_ideal_variables(url)
                except Exception as e:
                    if self._EtlPipeline__download_num_retries > 3:
                        logger.warning(f"Failed to find ideal variables, will retry")
                        continue
                    else:
                        logger.error(f"Failed to find ideal variables, there may have been an key mismatch. Error: {e}")
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
                        data_request = requests.get(data_url, headers=self.auth_header)

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
                        time.sleep(5)
                        continue
                    else:
                        logger.error(f"Got a 200 status code response from the API but failed the check for errors. Error: {e}")
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
        
        logger.info(f"Fishined downloading data for {self.name}")


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
            logger.error("No data was downloaded to be transformed for the CRD FlowWorks pipeline. This is not expected since it is the CRD FlowWorks Pipeline.")
            raise ValueError(f"No data exists in the _EtlPipeline__downloaded_data attribute! Expected at least a little.")

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
                #TODO Send Email
                raise RuntimeError(f"There was an error when trying to transform the data for {key}. Error: {e}")


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
            logger.error("No data was downloaded to be validated for the CRD FlowWorks pipeline. This is not expected since it includes the CRD FlowWorks Pipeline.")
            raise ValueError(f"No data exists in the _EtlPipeline__downloaded_data attribute! Expected at least a little.")

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
            logger.error("No data was downloaded to be loaded on to the database for the CRD FlowWorks pipeline. This is not expected since it includes the CRD FlowWorks Pipeline.")
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
        
        # Check if the env_vars exists:
        if not flowworks_credentials["UserName"] or not flowworks_credentials["Password"]:
            logger.error("FlowWorks credentials were not found in the environment variables.")
            raise ValueError("FlowWorks credentials were not found in the environment variables, please check the secrets.")
        
        headers = HEADER
        headers["Content-type"] = "application/json"
        
        try:

            token_post = requests.post(FLOWWORKS_TOKEN_URL, headers=headers, data=json.dumps(flowworks_credentials))
            
            if token_post.status_code != 200:
                raise RuntimeError(f"Post request for Auth token did not have status code 200! Got status: {token_post.status_code}")
            
            self.auth_header["Authorization"] = f"Bearer {token_post.json()}" 
        except Exception as e:
            logger.error(f"There was an error trying to get the FlowWorks Authorization token {e}")
            raise ValueError(f" There was an error trying to get the FlowWorks Authorization token {e}")

    def __get_flowworks_station_data(self):
        """
        FlowWorks requires us to work with their API, this is the function that will grab the station metadata and return it as a polars dataframe. This will not be needed to be done like
        this if we do not need to add any new stations. This will be discussed with Ben soon.

        Args:
            None

        Output:
            station_data (pl.LazyFrame): Polars LazyFrame object with Station metadata for stations that have been filtered by those in the database.
        """
        logger.info(f"Getting station data from the FlowWorks API")

        response = requests.get(self.source_url, headers=self.auth_header)

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
        station_data = (
            pl.LazyFrame(data_json["Resources"])
        )

        logger.debug(f"Checking for new stations that doesn't exist in the DB, if this fails, it will continue running the scraper without inserting new stations")
        try:
            self.get_and_insert_new_stations(station_data)
        except Exception as e:
            # TODO send email here
            logger.warning(f"Failed insert new stations, will continue running the scraper without inserting new stations. Error: {e}")    

        # Regardless of whether the insertion succeeds or not, filter the station data to only include stations that exist in the database
        station_data = station_data.filter(pl.col("Id").is_in(self.station_list.collect().get_column("original_id").cast(pl.Int64).to_list()))

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

    def __find_ideal_variables(self, url):
        """
        FlowWorks have a large number of variables. This function will find the ideal variables to scrape from the list of all variables. The 
        ideal variables are ranked in the FLOWWORKS_IDEAL_VARIABLES dict, which is defined in the constants file.

        Args:
            url (string): url to find data from

        Output:
            None
        """
        data_request = requests.get(url, headers=self.auth_header)

        # Check if the request response is 200
        if (data_request.status_code != 200):
            logger.error(f"Request status code was not 200! {data_request.status_code}, will raise an error")
            raise RuntimeError(f"Request status code was not 200! {data_request.status_code}")

        # Checking for any issues within API 
        try:
            self.__check_api_request_response(data_request.json())
        except (RuntimeError, KeyError) as e:
            logger.error(f"Got 200 response from API but failed to check for errors. Error: {e}")
            raise RuntimeError(f"Got 200 response from API but failed to check for errors. Error: {e}")

        logger.info(f"Finding ideal variables from FlowWorks Channels")
        df = pl.LazyFrame(data_request.json()["Resources"])

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

    def get_and_insert_new_stations(self, station_data):
        """
        This private method will check if there are any new stations in the downloaded data. If there are, then it will check that they are located within BC. If they are,
        then another check will be completed to see if they already exist under a different network id, if they do, only the new network_id will be inserted in to the database.
        If the station is completely new, all the metadata will be inserted in to the database.

        Args: 
            station_data (pl.LazyFrame): Polars LazyFrame object with Station metadata for all stations.

        Output: 
            None
        """
        # Adding columns in rename dict to make sure transformation happen alright. The values actually don't matter
        station_data = (
            station_data
            .with_columns(
                DataValue = pl.lit(0),
                DataTime = None,
                original_id = pl.col("Id").cast(pl.String),
            )
        )

        try:
            new_stations = self.check_for_new_stations({"station_data":station_data})
        except Exception as e:
            logger.error(f"Failed to check for new stations. Error: {e}")
            # TODO: Send email here
            raise RuntimeError(e)
        
        if new_stations.limit(1).collect().is_empty():
            logger.debug("No new stations found, going back to transformation")
            return
        
        new_stations = (
            new_stations
            .with_columns(Id = pl.col("original_id").str.slice(3).cast(pl.Int64))
            .join(station_data, on="Id", how="inner")
            .remove((pl.col("Latitude") == '') | (pl.col("Longitude") == '') | (pl.col("Name").str.contains("Demo")))
        )

        if new_stations.limit(1).collect().is_empty():
            logger.debug("No new stations that are not Demo stations, or stations without Lat, Lon were found. Going back to transformation")
            return
        
        # Check that the stations that were found are in BC
        try:
            in_bc = self.check_new_station_in_bc(new_stations.select("original_id", "Longitude", "Latitude"))
        except Exception as e:
            logger.error(f"Failed to check if new stations are in BC")
            raise RuntimeError(e)
        
        new_stations = new_stations.filter(pl.col("original_id").is_in(in_bc))

        if new_stations.limit(1).collect().is_empty():
            logger.debug("No new stations found in BC, going back to transformation")
            return
        
        # Check for stations that are found in different networks:
        different_network_station = (
            new_stations
            .filter(pl.col("station_id").is_not_null())
            .select("station_id")
            .unique()
        )

        if not different_network_station.limit(1).collect().is_empty():
            logger.debug(f"Found some stations in BC that are already in the database with different network ids. Inserting only the new network ids for these stations.")
            try:
                self.insert_only_station_network_id(different_network_station)
            except Exception as e:
                logger.error("Error when trying to insert only the new network ids for the stations that are already in the database with different network ids.")
                raise RuntimeError(e)
            
        new_stations = (
            new_stations
            .remove(pl.col("station_id").is_not_null())
        )
        
        if new_stations.limit(1).collect().is_empty():
            logger.info("No completely new stations found in the downloaded data. Going back to transformation")
            return
        
        # Get variables for the new stations
        url_dict = {station[2]:f"{self.source_url}{station[2]}/channels" for station in new_stations.collect().iter_rows()}

        var_id_dict = {"discharge":1, "stage":2, "temperature":7, "swe":16, "pc":28, "rainfall":29}
        station_variable = []
        station_type = []
        no_scrape = []
        for key in url_dict.keys():
            self.__find_ideal_variables(url_dict[key])

            # get variable names that don't have None as their value
            station_vars = [var for var in self.variable_to_scrape.keys() if self.variable_to_scrape[var]]
            # Map to their variable id
            station_vars = [*map(var_id_dict.get, station_vars)]
            
            # If there was nothing in the list, it should not be scraped
            if not station_vars:
                no_scrape.append(key)
                continue
            
            # If temperature is in the variables, add it's min and max
            if 7 in station_vars:
                station_vars.append(6)
                station_vars.append(8)
            
            station_variable.append((key, station_vars))

            # Station type, Hydrometric or Weather/Climate
            type_id = []
            if {1, 2}.intersection(set(station_vars)):
                type_id.append(1)
            if {7, 16, 28, 29}.intersection(set(station_vars)):
                type_id.append(3)
            
            station_type.append([key, type_id])

        # Construct the dataframe that will be fed in to the construction function
        new_stations = (
            new_stations
            .join(pl.LazyFrame(station_variable, schema={"original_id_right":pl.String, "variable_id": pl.List(pl.Int8)}, orient="row"), on="original_id_right", how="left")
            .join(pl.LazyFrame(station_type, schema={"original_id_right":pl.String, "type_id": pl.List(pl.Int8)}, orient="row"), on="original_id_right", how="left")
            .with_columns(
                scrape = pl.when(pl.col("Id").is_in(no_scrape))
                    .then(False)
                    .otherwise(True),
                station_status_id = 4,
                stream_name = pl.lit(''),
                operation_id = 2,
                drainage_area = None,
                regulated = False,
                user_flag = False,
                year = pl.when(pl.col("Id").is_in(no_scrape))
                    .then(None)
                    .otherwise([self.date_now.year]),
                project_id = [1, 3, 6],
                network_id = self.network
            )
            .select(
                pl.col("original_id"),
                pl.col("Longitude").alias("longitude"),
                pl.col("Latitude").alias("latitude"),
                pl.col("scrape"),
                pl.col("stream_name"),
                pl.col("InternalName").alias("station_name"),
                pl.col("Name").alias("station_description"),
                pl.col("station_status_id"),
                pl.col("operation_id"),
                pl.col("drainage_area"),
                pl.col("regulated"),
                pl.col("user_flag"),
                pl.col("project_id"),
                pl.col("network_id"),
                pl.col("type_id"),
                pl.col("variable_id"),
                pl.col("year")
            )
        )

        # Construct the insertion dataframes
        try:
            new_stations, insert_dict = self.construct_insert_tables(new_stations)
        except Exception as e:
            logger.error("Error when trying to construct the insertion dataframes.")
            raise RuntimeError(e)

        # Remove "HRB" Prefix or else the insertion will not insert anything
        for key in insert_dict.keys():
            insert_dict[key][1] = (
                insert_dict[key][1]
                .with_columns(original_id = pl.col("original_id").str.replace("HRB", ""))
            )
        # Insert the new stations into the database
        try:
            self.insert_new_stations(new_stations, insert_dict)
        except Exception as e:
            logger.error("Error when trying to insert new stations into the database.")
            raise RuntimeError(e)

        # TODO: Implement success emails
