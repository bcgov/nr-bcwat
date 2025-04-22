from abc import ABC, abstractmethod
from psycopg2.extras import execute_values
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class EtlPipeline(ABC):

    def __init__(self, name, source_url, destination_tables):
        # Public Attributes
        self.name = name
        self.source_url = source_url
        self.destination_tables = destination_tables
        
        #Private Attributes
        self.__download_num_retries = 0
        # __downloaded_data contains list of downloaded dataframes
        self.__downloaded_data = {}
        # __transformed_data contains the transformed dataframes
        self.__transformed_data = None

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

    def load_data(self):
        """
        Function to iterate through the destination tables and load the data into the database using the function __load_data_into_tables.

        Args:   
            None

        Output: 
            None
        """
        if self.__transformed_data is None:
            logger.warning("load_data is not implemented yet, exiting")
            return

        keys = self.destination_tables.keys()

        # Check that the destination tables have been populated
        if len(keys) == 0:
            logger.error(f"The scraper {self.name} did not give any tables to insert to! Exiting")
            raise RuntimeError(f"The scraper {self.name} did not give any tables to insert to! Exiting")

        for key in keys:
            # Check that the data to be inserted is not empty, if so, raise warning.
            if self.__transformed_data[key][0].is_empty():
                logger.Error(f"The data to be inserted into the table {self.destination_tables[key]} is empty! Skipping this table and raising error so it can be investigated.")
                raise RuntimeError(f"The data to be inserted into the table {self.destination_table[key]} is empty!")
            
            logger.debug(f"Loading data into the table {self.destination_tables[key]}")
            try:
                self.__load_data_into_tables(insert_tablename=self.destination_tables[key], data=self.__transformed_data[key][0], pkey=self.__transformed_data[key][1])
            except Exception as e:
                logger.error(f"Error loading data into the table {self.destination_tables[key]}")
                raise RuntimeError(f"Error loading data into the table {self.destination_tables[key]}. Error: {e}")

    def __load_data_into_tables(self, insert_tablename = None, data = pl.DataFrame(), pkey=None):
        """
        Private function that inserts the scraped data into the database. Checks have been put into place as well to ensure that 
        there is some data that is trying to be inserted. If there is not, it will raise an Error.

        Args:
            insert_tablename (str): The name of the table to insert data into (along with schema but that can be changed if needed)
            data (polars.DataFrame): The data to be inserted into the table in insert_tablename.
            pkey (list): A list of column names that are the primary keys of the table that is being inserted into.

        Output:
            None
        """
        if self.__transformed_data is None:
            logger.warning("__load_data_into_tables is not implemented yet, exiting")
            return

        try:
            # Getting the column names
            df_schema = data.schema.names()

            # Turning dataframe into insertable tuples.
            records = data.rows()

            # Creating the insert query
            insert_query = f"INSERT INTO {insert_tablename} ({', '.join(df_schema)}) VALUES %s ON CONFLICT ({', '.join(pkey)}) DO UPDATE SET value = EXCLUDED.value;"
            
            ### How this connection is got will change once this is in Airflow
            # cursor = db.cursor()
            cursor = self.db_conn.cursor()

            logger.debug(f'Inserting {len(records)} rows into the table {insert_tablename}')
            execute_values(cursor, insert_query, records, page_size=100000)
            
            # db.conn.commit()
            self.db_conn.commit()
        except Exception as e:
            logger.error(f"Inserting into the table {insert_tablename} failed!")
            raise RuntimeError(f"Inserting into the table {insert_tablename} failed! Error: {e}")

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

