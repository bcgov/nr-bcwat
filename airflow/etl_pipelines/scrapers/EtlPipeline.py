from abc import ABC, abstractmethod
from psycopg2.extras import execute_values
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class EtlPipeline(ABC):

    def __init__(
            self,
            name=None,
            source_url=None,
            destination_tables={},
            expected_dtype=None,
            db_conn=None
        ):
        # Public Attributes
        self.name = name
        self.source_url = source_url
        self.destination_tables = destination_tables
        self.expected_dtype = expected_dtype
        self.db_conn = db_conn

        #Private Attributes
        self.__download_num_retries = 0
        # __downloaded_data contains list of downloaded dataframes
        self.__downloaded_data = {}
        # __transformed_data contains the transformed dataframes
        self.__transformed_data = {}

    @abstractmethod
    def download_data(self):
        """Download data files from URLs"""
        pass

    @abstractmethod
    def validate_downloaded_data(self):
        """Check that the downloaded data is valid and shaped correctly"""
        pass

    @abstractmethod
    def transform_data(self):
        """Apply the required transformation for the data that was downloaded"""
        pass

    @abstractmethod
    def _load_data_into_tables(self, insert_tablename=None, data=pl.DataFrame(), pkey=None):
        """Load data into the destination table."""
        pass

    def load_data(self):
        """
        Function to iterate through the destination tables and load the data into the database using the function __load_data_into_tables.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Loading data into the destination tables for {self.name}")

        transformed_data = self.get_transformed_data()

        keys = transformed_data.keys()

        # Check that the destination tables have been populated
        if len(self.destination_tables.keys()) == 0:
            logger.warning(f"The scraper {self.name} did not give any tables to insert to! This may be expected depending on the scraper. Please check for any previous errors or warnings. Exiting")
            return

        for key in keys:
            # Check that the data to be inserted is not empty, if so, raise warning.
            if transformed_data[key]["df"].is_empty():
                logger.warning(f"The data to be inserted into the table {self.destination_tables[key]} is empty! Skipping this table and moving on.")
                # TODO: Implement email to notify that this happened.
                continue

            logger.debug(f"Loading data into the table {self.destination_tables[key]}")
            try:
                self._load_data_into_tables(insert_tablename=self.destination_tables[key], data=transformed_data[key]["df"], pkey=transformed_data[key]["pkey"], truncate=transformed_data[key]["truncate"])
            except Exception as e:
                logger.error(f"Error loading data into the table {self.destination_tables[key]}")
                raise RuntimeError(f"Error loading data into the table {self.destination_tables[key]}. Error: {e}")

    def get_downloaded_data(self):
        """
        A getter function for the private attribute __downloaded_data.

        Args:
            None

        Output:
            __downloaded_data (list): List of downloaded dataframes
        """
        logger.debug(f"Getting downloaded data")
        return self.__downloaded_data

    def get_transformed_data(self):
        """
        A getter function for the private attribute __transformed_data.

        Args:
            None

        Output:
            __transformed_data (dict): Dictionary of transformed dataframes
        """
        logger.debug(f"Getting transformed data")
        return self.__transformed_data

    def validate_downloaded_data(self):
        """
        Check the data that was downloaded to make sure that the column names are there and that the data types are as expected.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Validating the dowloaded data's column names and dtypes.")
        downloaded_data = self.get_downloaded_data()

        keys = list(downloaded_data.keys())
        if len(keys) == 0:
            raise ValueError(f"No data was downloaded! Please check and rerun")

        for key in keys:
            if key not in self.expected_dtype:
                raise ValueError(f"The correct key was not found in the column validation dict! Please check: {key}")

            columns = downloaded_data[key].collect_schema().names()
            dtypes = downloaded_data[key].collect_schema().dtypes()

            if not columns  == list(self.expected_dtype[key].keys()):
                raise ValueError(f"One of the column names in the downloaded dataset is unexpected! Please check and rerun.\nExpected: {self.expected_dtype[key].keys()}\nGot: {columns}")

            if not dtypes == list(self.expected_dtype[key].values()):
                raise TypeError(f"The type of a column in the downloaded data does not match the expected results! Please check and rerun\nExpected: {self.expected_dtype[key].values()}\nGot: {dtypes}")

        logger.info(f"Validation Passed!")
