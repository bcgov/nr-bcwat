from utils.eltpipeline_class import EtlPipeline
from utils.constants import (
    logger,
    DB_URI,
    HEADER,
    FAIL_RATIO
)
import polars as pl
import requests
import os
from datetime import datetime

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
        for url in self.source_url:
            logger.debug(f"Downloading data from URL: {url[1]}")
            # Within function retry, will only retry once.
            is_retry = False
            while True:
                try:
                    # Stream is True so that we can download directly to memory
                    response = requests.get(url[1], stream=True, headers=HEADER, timeout=20)
                    break
                except requests.exceptions.RequestException as e:
                    if is_retry == False:
                        continue
                    else:
                        logger.error(f"Error downloading data from URL: {url[1]}. Error: {e}")
                        failed_downloads += 1
                        break
            # If the last attempt was a retry, skip station.
            if is_retry:
                continue

            # Check if the response is 200
            if response.status_code != 200:
                logger.warning(f"Link status code is not 200 with URL {url[1]}, continuing to next station")
                failed_downloads += 1
                continue
            
            try:
                logger.debug('Got response from URL, loading data into DataFrame')
                response.raw.decode_content = True
                data_df = pl.scan_csv(response.raw, infer_schema=True, infer_schema_length=100, has_header=True)
            except Exception as e:
                logger.error(f"Error when loading csv data in to LazyFrame, error: {e}")
                failed_downloads += 1
                continue
            
            # Check if the data is empty
            if data_df.limit(1).collect().is_empty():
                logger.warning(f"Downloaded data is empty for URL: {url[1]}. Will not mark as failure but be noted.")
                continue

            # __downloaded_data contains the path to the downloaded data if go_through_all_stations is False
            if not self.go_through_all_stations:
                self._EtlPipeline__downloaded_data.append({url[0]:data_df})

        # Check if the number of failed downloads is greater than 50% of the total number of downloads if it is, the warnings are promoted to errors
        if failed_downloads/len(self.source_url) > FAIL_RATIO:
            logger.error(f"More than 50% of the data was not downloaded, exiting")
            raise RuntimeError(f"More than 50% of the data was not downloaded. {failed_downloads} out of {len(self.source_url)} failed to download. for {self.name} pipeline")

    def get_station_list(self, station_source = None):
        """
        Queries the database to get the list of stations that uses the station_source value as it's data source.

        Args:
            station_source (string): String that indicates the group of stations to get

        Output:
            polars.LazyFrame(): Polars LazyFrame object with the station_id and internal_station_id as the columns.
        """
        if station_source is None:
            logger.warning("get_station_list is not implemented yet, exiting")
            return

        logger.debug(f"Gathering Stations from Database using station_source: {station_source}")

        query = f""" SELECT original_id, station_id FROM  bcwat_obs.scrape_station WHERE  station_data_source = '{station_source}';"""

        return pl.read_database_uri(query, DB_URI).lazy()
        

class DataBcPipeline(EtlPipeline):
    def __init__(self, name, url, destination_tables, databc_layer_name):
        # Initializing attributes in parent
        super().__init__(name=name, source_url=url, destination_tables=destination_tables)

        # Initializing attributes in child
        self.databc_layer_name = databc_layer_name
        # Private attribute
        self.__downloaded_data = None

    def download_data(self):
        logger.warning("download_data is not implemented yet, exiting")
        pass
