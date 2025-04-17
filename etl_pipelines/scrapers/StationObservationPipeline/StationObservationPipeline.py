from scrapers.EtlPipeline import EtlPipeline
from utils.constants import (
    logger,
    HEADER,
    FAIL_RATIO,
    MAX_NUM_RETRY
)
from utils.database import db
import polars as pl
import requests
from time import sleep

class StationObservationPipeline(EtlPipeline):
    def __init__(self, name, source_url, destination_tables):
        # Initializing attributes in parent class
        super().__init__(name=name, source_url=source_url, destination_tables=destination_tables)

        # Initializing attributes present class
        self.station_list = None
        self.go_through_all_stations = False

    def download_data(self):
        """
        Implementation of the download_data function for the StationObservationPipeline class. This function downloads the data from the URLs provided by the source_url attribute.
        It uses the requests library to download the data and the polars library to steam the data into a LazyFrame. The function also handles errors and retries the download if it fails.

        Args: 
            None

        Output: 
            None
        """
        if self.source_url == "tempurl":
            logger.warning("Not implemented yet, exiting")
            return
        
        failed_downloads = 0
        keys = self.source_url.keys()
        for key in keys:
            self._EtlPipeline__download_num_retries = 0
            failed = False

            logger.debug(f"Downloading data from URL: {self.source_url[key]}")
            # Within function retry, will only retry once.
            while True:
                try:
                    # Stream is True so that we can download directly to memory
                    response = requests.get(self.source_url[key], stream=True, headers=HEADER, timeout=20)
                except requests.exceptions.RequestException as e:
                    if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                        logger.warning(f"Error downloading data from URL: {self.source_url[key]}. Retrying...")
                        self._EtlPipeline__download_num_retries += 1
                        sleep(5)
                        continue
                    else:
                        logger.error(f"Error downloading data from URL: {self.source_url[key]}. Error: {e}")
                        failed = True
                        break
                
                # Check if response is 200
                if response.status_code == 200:
                    logger.debug(f"Request got 200 response code, moving on to loading data")
                    break
                elif self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Link status code is not 200 with URL {self.source_url[key]}. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(5)
                    continue
                else:
                    logger.warning(f"Link status code is not 200 with URL {self.source_url[key]}, continuing to next station")
                    failed = True
                    break
            
            # If failed flag is True them increment filed_downloads by 1 and move on to next URL
            if failed:
                logger.warning(f"The URL {self.source_url[key]} failed to download 3 times, moving on to next URL")
                failed_downloads += 1
                continue
            
            ## This may have to change since not all sources are CSVs
            try:
                logger.debug('Got response from URL, loading data into LazyFrame')
                response.raw.decode_content = True
                data_df = pl.scan_csv(response.raw, infer_schema=True, infer_schema_length=100, has_header=True, schema_overrides=self.expected_dtype)
            except Exception as e:
                logger.error(f"Error when loading csv data in to LazyFrame, error: {e}")
                failed_downloads += 1
                continue
            
            # Check if the data is empty
            if data_df.limit(1).collect().is_empty():
                logger.warning(f"Downloaded data is empty for URL: {self.source_url[key]}. Will not mark as failure but be noted.")
                continue

            # __downloaded_data contains the path to the downloaded data if go_through_all_stations is False
            if not self.go_through_all_stations:
                self._EtlPipeline__downloaded_data[key] = data_df

        # Check if the number of failed downloads is greater than 50% of the total number of downloads if it is, the warnings are promoted to errors
        if failed_downloads/len(self.source_url.keys()) > FAIL_RATIO:
            logger.error(f"More than 50% of the data was not downloaded, exiting")
            raise RuntimeError(f"More than 50% of the data was not downloaded. {failed_downloads} out of {len(self.source_url.keys())} failed to download. for {self.name} pipeline")

    def get_station_list(self):
        """
        Queries the database to get the list of stations that uses the station_source value as it's data source.

        Args:
            station_source (string): String that indicates the group of stations to get

        Output:
            polars.LazyFrame(): Polars LazyFrame object with the station_id and internal_station_id as the columns.
        """
        if self.station_source is None:
            logger.warning("get_station_list is not implemented yet, exiting")
            return

        logger.debug(f"Gathering Stations from Database using station_source: {self.station_source}")

        query = f""" SELECT original_id, station_id FROM  bcwat_obs.scrape_station WHERE  station_data_source = '{self.station_source}';"""

        self.station_list = pl.read_database(query, connection=db.conn).lazy()

    def validate_downloaded_data(self):
        """
        Check the data that was downloaded to make sure that the column names are there and that the data types are as expected.

        Args:
            None

        Output:
            None
        """
        logger.debug(f"Validating the dowloaded data's column names and dtypes.")
        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            raise ValueError(f"No data was downloaded! Please check and rerun")
        
        keys = list(downloaded_data.keys())
        columns = downloaded_data[keys[0]].collect_schema().names()
        dtypes = downloaded_data[keys[0]].collect_schema().dtypes()

        if not columns  == self.validate_column:
            raise ValueError(f"One of the column names in the downloaded dataset is unexpected! Please check and rerun")
        print(dtypes)
        if not dtypes == self.validate_dtype:
            raise TypeError(f"The type of a column in the downloaded data does not match the expected results! Please check and rerun")
