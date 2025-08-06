from etl_pipelines.scrapers.EtlPipeline import EtlPipeline
from etl_pipelines.utils.constants import (
    MAX_NUM_RETRY,
    EXPECTED_UNITS,
    BC_WLS_WRL_WRA_COLUMN_ORDER
)
from etl_pipelines.utils.functions import setup_logging, reconnect_if_dead
from psycopg2.extras import execute_values
from time import sleep
import polars_st as st
import polars as pl
import pendulum
import bcdata
import geopandas as gpd


logger = setup_logging()

class DataBcPipeline(EtlPipeline):
    def __init__(
        self,
        name,
        destination_tables,
        url=None,
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
        """
        Method that downloads data from DataBC using the bcdata package. It takes the databc_layer_name attribute of the class and
        uses it to download the corresponding data from DataBC. If the databc_layer_name is not set, it will raise an error.
        The data is downloaded in GeoPandas format, which is converted to a polars_st GeoLazyFrame. The column names are converted to
        be lowercase since they are all uppercase by default.
        If there is no data returned from DataBC, it will retry up to MAX_NUM_RETRY times.

        Args:
            None

        Output:
            None
        """
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
                    sleep(120)
                    continue

                else:
                    logger.error(f"Error trying to get data from DataBC using bcdata! Error{e}", exc_info=True)
                    raise RuntimeError(f"Error tyring to get data from DataBC using bcdata! Error{e}")

            # Check that there is actually any data in the st.GeoDataFrame
            if gdf.limit(1).collect().is_empty():
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"No data was returned from bcdata for {self.name}, retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(120)
                    continue
                else:
                    logger.error(f"No data was returned from bcdata for {self.name}, exiting and failing.")
                    raise RuntimeError(f"No data was returned from bcdata for {self.name}, exiting and failing.")
            else:
                logger.info(f"Got {self.databc_layer_name} data from DataBC. Moving on...")
                break

        self._EtlPipeline__downloaded_data[self.databc_layer_name] = gdf

        logger.info(f"Finished downloading data for {self.name}")

    def _load_data_into_tables(self, insert_tablename=None, data=pl.DataFrame(), pkey=None, truncate=False):
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
            self.db_conn  = reconnect_if_dead(self.db_conn)
            cursor = self.db_conn.cursor()

            # If the truncate flag is set to True, truncate the table before inserting. Else just insert.
            if truncate:
                logger.info(f"Truncate flag is True, Truncating the table before inserting.")
                cursor.execute(f"TRUNCATE TABLE {insert_tablename};")

            logger.debug(f'Inserting {len(records)} rows into the table {insert_tablename}')
            execute_values(cursor, insert_query, records, page_size=100000)

            self.db_conn.commit()

            cursor.close()
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Inserting into the table {insert_tablename} failed!")
            raise RuntimeError(f"Inserting into the table {insert_tablename} failed! Error: {e}")

    def get_whole_table(self, table_name, has_geom=False):
        """
        Method that returns a LazyFrame of an entire table. The table_name should be the name of the table without the schema.

        Args:
            table_name (str): The name of the table to get the data from.
            has_geom (bool): Whether or not the table has a geom4326 column. Defaults to False.

        Output:
            polars.LazyFrame: LazyFrame with the data from the table. If the has_geom flag is True, then the geojson column will be added, which is a column with the geometry data in GeoJSON format.
        """
        logger.info(f"Getting {table_name} Data from database")
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

        return pl.read_database(query=query, connection=self.db_conn, infer_schema_length=None).lazy()

    def update_import_date(self, data_source_name):
        """
        Method that updates the import date for the given data source name.

        Args:
            data_source_name (str): The name of the data source to be updated in the bc_data_import_date table.

        Output:
            None
        """

        try:
            query = f"""
                UPDATE
                    bcwat_lic.bc_data_import_date
                SET
                    import_date = CURRENT_DATE
                WHERE
                    dataset = '{data_source_name}';
            """
            self.db_conn  = reconnect_if_dead(self.db_conn)
            cursor = self.db_conn.cursor()
            cursor.execute(query)
            self.db_conn.commit()
            cursor.close()

        except Exception as e:
            cursor.close()
            self.db_conn.rollback()
            logger.error(f"Updating import date for {data_source_name} failed!")
            raise RuntimeError(f"Updating import date for {data_source_name} failed! Error: {e}")

    def _check_for_new_units(self, new_rows):
        """
        This function takes a DF of new rows and checks if there are any new units associated with the data.
        If there are new units, it logs a warning with the list of new units found and asks the user to check them and manually adjust the code and units if necessary.

        Args:
            new_rows (pl.DataFrame): Polars DataFrame with all the rows obtained from DataBC that will be inserted in to the DB

        Output:
            None
        """
        new_units = (
            new_rows
            .filter(
                (~pl.col("units").is_in(EXPECTED_UNITS))
            )
            .get_column("units")
            .unique()
            .to_list()
        )

        if new_units:
            logger.warning(f"""New units were found in the inserted data for {self.name}! Please check them and adjust the code accordingly.

                           If these units are not expected, please edit these values in the quantity_units, or qty_units_diversion_max_rate columns and it's associated value columns: quantity, and qty_diversion_max_rate in the table bcwat_lic.bc_wls_water_approval if the scraper name is "Water Approval Points".

                           If the scraper name is "Water Rights Applications Public " or "Water Rights Licences Public " then please adjust the column qty_units and it's associated value column qty_original in bcwat_lic.bc_wls_wrl_wra table manually with the correct conversions to the associated values.

                           Units Found: {', '.join(new_units)}""")

            # TODO: Implement email to notify that this happened if implementing email notifications.

    def transform_bc_wls_wrl_wra_data(self):

        """
        This function takes the bcwat_lic.bc_water_rights_applications_public, and bcwat_lic.bc_water_rights_licences_public tables
        and combines them into one table.

        If either of the tables are missing an column, it is added on by creating a column filled with Null values.

        The import dates of the two tables are checked to make sure they are the same. If they are not, then a ValueError is thrown.

        Args:
            None

        Output:
            None
        """
        logger.info("Start of combining bcwat_lic.bc_water_rights_applications_public, and bcwat_lic.bc_water_rights_licences_public for insertion to main table.")

        try:
            logger.debug("Gathering import dates for the two tables to make sure that the impor dates are the same.")

            # Get the import_date values for the water_rights_applications_public and water_rights_licences_public so that we know we're joining the
            # latest data.
            import_date_table = self.get_whole_table(table_name="bc_data_import_date", has_geom=False).collect()

            # Extract the dates from the DataFrame

            wrap_import_date = import_date_table.filter(pl.col("dataset") == pl.lit("water_rights_applications_public")).get_column("import_date").item()
            wrlp_import_date = import_date_table.filter(pl.col("dataset") == pl.lit("water_rights_licences_public")).get_column("import_date").item()
        except Exception as e:
            logger.error(f"Failed to get the bc_data_import_date table from the database. Please check the errors {e}")
            raise RuntimeError(f"Failed to get the bc_data_import_date table from the database. Please check the errors {e}")

        # Compare and throw exception if the dates aren't the same
        if wrap_import_date != wrlp_import_date:
            logger.error(f"""The import dates for water_rights_applications_public and water_rights_licences_public are not the same. This means that either one of the scraping steps failed and did not get caught. Please check the one out of sync with the current date. \n Water Rights Licences Public Import Date: {wrlp_import_date} \n Water Rights Applications Public Import Date: {wrap_import_date} \n Current Date: {self.date_now.date()}""")
            raise ValueError(f"""The import dates for water_rights_applications_public and water_rights_licences_public are not the same. This means that either one of the scraping steps failed and did not get caught. Please check the one out of sync with the current date. \n Water Rights Licences Public Import Date: {wrlp_import_date} \n Water Rights Applications Public Import Date: {wrap_import_date} \n Current Date: {self.date_now.date()}""")

        # Get the data that was inserted in the previous steps of the scraper from the database.
        try:
            logger.debug(f"Collecting the tables themselves to be reshaped and merged in to one.")

            bc_wrap = self.get_whole_table(table_name="bc_water_rights_applications_public", has_geom=True)
            bc_wrlp = self.get_whole_table(table_name="bc_water_rights_licences_public", has_geom=True)

            coverage_polygon = st.from_geopandas(
                gpd.read_postgis(
                    sql="SELECT geom4326 AS poly FROM bcwat_lic.water_licence_coverage",
                    con=self.db_conn,
                    geom_col="poly",
                    crs="EPSG:4326"
                )
            ).lazy()
        except Exception as e:
                logger.error(f"Failed to get either the table bcwat_lic.bc_water_rights_applications_public or bcwat_lic.bc_water_rights_licences_public from the database! Please investigate {e}")
                raise RuntimeError(f"Failed to get either the table bcwat_lic.bc_water_rights_applications_public or bcwat_lic.bc_water_rights_licences_public from the database! Please investigate {e}")

        try:

            logger.debug("Altering the LazyFrame bc_wrap")
            # Do some transformations to both bc_wrap and bc_wrlp.
            bc_wrap = (
                bc_wrap
                # The DataBC layer that we get this data from is missing a lot of the columns so we fill it with Null Values.
                .with_columns(
                    wls_wrl_wra_id = pl.col("wrap_id"),
                    pcl_no = pl.lit(None).cast(pl.String),
                    qty_original = pl.lit(None).cast(pl.Float64),
                    qty_flag = pl.lit(None).cast(pl.String),
                    qty_units = pl.lit(None).cast(pl.String),
                    lic_status_date = pl.lit(None).cast(pl.Date),
                    priority_date = pl.lit(None).cast(pl.Date),
                    expiry_date = pl.lit(None).cast(pl.Date),
                    stream_name = pl.lit(None).cast(pl.String),
                    quantity_day_m3 = pl.lit(None).cast(pl.Float64),
                    quantity_sec_m3 = pl.lit(None).cast(pl.Float64),
                    quantity_ann_m3 = pl.lit(None).cast(pl.Float64),
                    rediversion_flag = pl.lit(None).cast(pl.String),
                    flag_desc = pl.lit(None).cast(pl.String),
                    water_source_type_desc = pl.lit(None).cast(pl.String),
                    hydraulic_connectivity = pl.lit(None).cast(pl.String),
                    related_licences = pl.lit(None).cast(pl.List(pl.String)),
                    ann_adjust = pl.lit(None).cast(pl.Float64),
                    geom4326 = st.from_geojson(pl.col("geojson")).st.set_srid(4326)
                )
                # This constant is a list of strings that makes it easier to change the order of the columns
                .select(BC_WLS_WRL_WRA_COLUMN_ORDER)
            )

            logger.debug("Altering the LazyFrame bc_wrlp")

            bc_wrlp = (
                bc_wrlp
                # This DataBC layer has most of the columns, so only minor changes have to be made.
                .with_columns(
                    wls_wrl_wra_id = pl.col("wrlp_id"),
                    geom4326 = st.from_geojson(pl.col("geojson")).st.set_srid(4326),
                    qty_diversion_max_rate = pl.col("qty_diversion_max_rate").cast(pl.Float64)
                )
                .select(BC_WLS_WRL_WRA_COLUMN_ORDER)
            )

            # Concat the table together so that they are one DataFrame for the following transformations
            bc_wls_wrl_wra = (
                pl.concat([bc_wrap, bc_wrlp])
                .join_where(
                    coverage_polygon,
                    pl.col("poly").st.contains(pl.col("geom4326"))
                )
                .drop("poly")
                .collect()
            )

        except Exception as e:
            logger.error(f"Failed to join bc_wrap and bc_wrlp LazyFrames with addition of extra columns! Please check {e}")
            raise RuntimeError(f"Failed to join bc_wrap and bc_wrlp LazyFrames with addition of extra columns! Please check {e}")

        if bc_wls_wrl_wra.is_empty():
            logger.error("The combine step of the water rights licences public and water rights applications public failed. There should not be 0 entries in this dataframe. Please check and debug.")
            raise ValueError(f"The combine step of the water rights licences public and water rights applications public failed. There should not be 0 entries in this dataframe. Please check and debug.")
        elif bc_wls_wrl_wra.shape[0] < 25000:
            logger.warning(f"After combining the data from bcwat_lic.bc_water_rights_applications_public, and bcwat_lic.bc_water_rights_licences_public, there were less than 50, 000 licences left to insert. This is less than expected, so will not update the table bcwat_lic.bc_wls_wrl_wra!")
            return
        else:
            self._EtlPipeline__transformed_data["final_table"] = {"df": bc_wls_wrl_wra, "pkey": ["wls_wrl_wra_id"], "truncate": True}

        try:
            self._check_for_new_units(
                (
                    bc_wls_wrl_wra
                    .select(
                        pl.col("qty_units").alias("units")
                    )
                )
            )
        except Exception as e:
            logger.error(f"There was an issue checking if there were new units in the rows to be inserted for the combine function for bc_wls_wrl_wra! Error: {e}")
            raise RuntimeError(f"There was an issue checking if there were new units in the rows to be inserted for the combine function for bc_wls_wrl_wra! Error: {e}")


        logger.info("Finished combining bcwat_lic.bc_water_rights_applications_public, and bcwat_lic.bc_water_rights_licences_public tables.")
