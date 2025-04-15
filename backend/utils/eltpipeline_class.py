from abc import ABC, abstractmethod
from utils.database import db
from psycopg2.extras import execute_values
from utils.constants import (
    logger,
    DB_URI
)
import polars as pl

class EtlPipeline(ABC):

    def __init__(self, name, source_url, destination_tables):
        # Public Attributes
        self.name = name
        self.source_url = source_url
        self.destination_tables = destination_tables
        
        #Private Attributes
        self.__download_num_retries = 0
        # __downloaded_data contains list of downloaded dataframes
        self.__downloaded_data = []
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
        A getter function for the private function __load_data_into_tables.

        Args:   
            None

        Output: 
            None
        """
        if self.__transformed_data is None:
            logger.warning("load_data is not implemented yet, exiting")
            return

        logger.debug(f"Loading data into tables: {", ".join(self.destination_tables.values())}")
        self.__load_data_into_tables()

    def __load_data_into_tables(self):
        """
        
        """
        if self.__transformed_data is None:
            logger.warning("__load_data_into_tables is not implemented yet, exiting")
            return

        insert_keys = self.destination_tables.keys()

        for df_type in insert_keys:
            insert_table_name = self.destination_tables[df_type]

            logger.debug(f"Materializing LazyFrame for table {insert_table_name}")
            try:
                df = self.__transformed_data[df_type][0].collect()
                pkey = self.__transformed_data[df_type][1]
            except Exception as e:
                logger.error(f"There was an issue materializing the DataFrame from the LazyFrame for the table {insert_table_name}", exc_info=True)
                raise RuntimeError(f"There was an issue materializing the DataFrame from the LazyFrame for the table {insert_table_name}. Error: {e}")

            logger.debug(f'Inserting {df_type} data into the table {insert_table_name}')
            try:
                # Getting the column names
                df_schema = df.schema.names()

                records = df.rows()

                # Creating the insert query
                insert_query = f"INSERT INTO {insert_table_name} ({', '.join(df_schema)}) VALUES %s ON CONFLICT ({', '.join(pkey)}) DO UPDATE SET value = EXCLUDED.value;"

                cursor = db.conn.cursor()

                execute_values(cursor, insert_query, records, page_size=100000)
                
                db.conn.commit()
            except Exception as e:
                logger.error(f"Inserting into the table {insert_table_name} failed!")
                raise RuntimeError(f"Inserting into the table {insert_table_name} failed! Error: {e}")

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

