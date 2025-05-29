from etl_pipelines.scrapers.EtlPipeline import EtlPipeline
from etl_pipelines.utils.constants import (
    MAX_NUM_RETRY
)
from etl_pipelines.utils.functions import setup_logging
from psycopg2.extras import execute_values
import polars_st as st
import polars as pl
import pendulum
import bcdata

logger = setup_logging()

class DataBcPipeline(EtlPipeline):
    def __init__(
        self,
        name,
        url,
        destination_tables,
        databc_layer_name=None,
        expected_dtype=None,
        db_conn=None,
        date_now=pendulum.now("UTC")
    ):
        # Initializing attributes in parent
        super().__init__(
            name=name,
            source_url=url,
            destination_tables=destination_tables,
            expected_dtype = expected_dtype,
            db_conn=db_conn
        )

        # Initializing attributes in child
        self.date_now = date_now
        self.databc_layer_name = databc_layer_name

    def download_data(self):
        logger.info(f"Using bcdata to download data from DataBC for {self.name}")

        if not self.databc_layer_name:
            logger.error(f"No databc_layer_name provided for {self.name}")
            raise RuntimeError(f"No databc_layer_name provided for {self.name}")

        while True:
            try:
                # Use the bcdata package to get the layer from DataBC in GeoPandas format. Then transform that GeoDataFrame into a polars_st
                # GeoDataFrame.
                gdf = st.from_geopandas(bcdata.get_data(self.databc_layer_name, as_gdf=True), schema_overrides=self.expected_dtype[self.databc_layer_name]).lazy()
                # Convert column names to be lowercase since tey are all uppercase by default.
                gdf = gdf.rename(str.lower)
            except Exception as e:
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Failed trying to download data from DataBC using bcdata for {self.name}. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    continue

                else:
                    logger.error(f"Error trying to get data from DataBC using bcdata! Error{e}", exc_info=True)
                    raise RuntimeError(f"Error tyring to get data from DataBC using bcdata! Error{e}")

            # Check that there is actually any data in the st.GeoDataFrame
            if gdf.limit(1).collect().is_empty():
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"No data was returned from bcdata for {self.name}, retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    continue
                else:
                    logger.error(f"No data was returned from bcdata for {self.name}, exiting and failing.")
                    raise RuntimeError(f"No data was returned from bcdata for {self.name}, exiting and failing.")
            else:
                logger.info(f"Got {self.databc_layer_name} data from DataBC. Moving on...")
                break

        self._EtlPipeline__downloaded_data[self.databc_layer_name] = gdf

        logger.info(f"Finished downloading data for {self.name}")

    def _load_data_into_tables(self, insert_tablename=None, data=pl.DataFrame(), pkey=None):
        """
        Class instance function that inserts the scraped data into the database. A little different from the StationObservationPipeline
        because it does not update if there is a conflict with the primary key.

        Args:
            insert_tablename (str): The name of the table to insert data into (along with schema but that can be changed if needed)
            data (polars.DataFrame): The data to be inserted into the table in insert_tablename.
            pkey (list): A list of column names that are the primary keys of the table that is being inserted into.

        Output:
            None
        """
        try:
            # Getting the column names
            df_schema = data.schema.names()

            # Turning dataframe into insertable tuples.
            records = data.rows()

            # Creating the insert query
            insert_query = f"INSERT INTO {insert_tablename} ({', '.join(df_schema)}) VALUES %s ON CONFLICT ({', '.join(pkey)}) DO NOTHING;"

            cursor = self.db_conn.cursor()

            logger.debug(f'Inserting {len(records)} rows into the table {insert_tablename}')
            execute_values(cursor, insert_query, records, page_size=100000)

            self.db_conn.commit()

            cursor.close()
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Inserting into the table {insert_tablename} failed!")
            raise RuntimeError(f"Inserting into the table {insert_tablename} failed! Error: {e}")

    def get_whole_table(self, table_name, has_geom=False):
        if has_geom:
            query = f"""
                SELECT
                    ({table_name}).*,
                    ST_AsGeoJSON(geom4326) AS geojson
                FROM
                    bcwat_lic.{table_name}
            """

        else:
            query = f"""
                SELECT
                    *
                FROM
                    bcwat_lic.{table_name}
            """

        return pl.read_database(query=query, connection=self.db_conn).lazy()

