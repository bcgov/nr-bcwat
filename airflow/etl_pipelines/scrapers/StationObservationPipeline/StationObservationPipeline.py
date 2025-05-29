from abc import abstractmethod
from etl_pipelines.scrapers.EtlPipeline import EtlPipeline
from etl_pipelines.utils.constants import (
    HEADER,
    FAIL_RATIO,
    MAX_NUM_RETRY,
    NEW_STATION_INSERT_DICT_TEMPLATE
)
from etl_pipelines.utils.functions import setup_logging
from psycopg2.extras import execute_values, RealDictCursor
import polars as pl
import requests
import pendulum
import json
from time import sleep

logger = setup_logging()

class StationObservationPipeline(EtlPipeline):
    def __init__(
            self,
            name=None,
            source_url=None,
            destination_tables={},
            days=2,
            station_source=None,
            expected_dtype={},
            column_rename_dict={},
            go_through_all_stations=False,
            overrideable_dtype = False,
            network_ids=[],
            min_ratio={},
            db_conn=None,
            date_now=pendulum.now("UTC")
        ):
        # Initializing attributes in parent class
        super().__init__(
            name=name,
            source_url=source_url,
            destination_tables=destination_tables,
            expected_dtype = expected_dtype,
            db_conn=db_conn
        )

        # Initializing attributes present class
        self.station_list = None
        self.no_scrape_list = None
        self.days = days
        self.station_source = station_source
        self.column_rename_dict = column_rename_dict
        self.go_through_all_stations = go_through_all_stations
        self.overideable_dtype = overrideable_dtype
        self.network = network_ids
        self.no_scrape_list = None
        self.min_ratio = min_ratio

        # Setup date variables
        self.date_now = date_now.in_tz("UTC")
        self.end_date = self.date_now.in_tz("America/Vancouver")
        self.start_date = self.end_date.subtract(days=self.days).start_of("day")

        # Collect station_ids
        self.get_station_list()

    @abstractmethod
    def get_and_insert_new_stations(self, station_data = None):
        pass

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

        logger.info(f"Starting data file download for {self.name}")

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
                    # If it is the DriveBC scraper, then check if the response is 200 AND if the "text" attribute is empty. This can happen sometimes, and if it does, needs to be retried.
                    if self.station_source == "moti":

                        # If this scraper has retried 3 times then exit with a failed download
                        if self._EtlPipeline__download_num_retries > MAX_NUM_RETRY:
                            logger.error(f"Error downloading data from URL: {self.source_url[key]}. Used all retries, exiting with failure")
                            failed = True
                            break

                        # Check if response is 200 and isn't empty text:
                        elif response.text == "":
                            logger.warning(f"Response status code was 200 but the text was empty, retrying to see if we can get data.")
                            self._EtlPipeline__download_num_retries += 1
                            sleep(5)
                            continue

                        # Check if the message "No SAWS weather data found" is in the text
                        elif "No SAWS weather data found" in response.text:
                            logger.warning(f"Response status code was 200 but the message:\nNo SAWS weather data found\n was in the text. Going to retry with a longer timeout.")
                            self._EtlPipeline__download_num_retries += 1
                            sleep(30)
                            continue

                        # Check if the message "Could not retrieve SAWS report data" is in the text
                        elif "Could not retrieve SAWS report data" in response.text:
                            logger.error("MOTI returned a 200 status code but has message:\nCould not retrieve SAWS report data\nExiting with failure")
                            failed = True
                            break

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
                logger.debug('Loading data into LazyFrame')
                response.raw.decode_content = True

                # Call the private method that will load the data into a LazyFrame in the correct way depending on the scraper.
                data_df = self.__make_polars_lazyframe(response, key)

            except Exception as e:
                logger.error(f"Error when loading data in to LazyFrame, error: {e}")
                failed_downloads += 1
                continue

            # Check if the data is empty
            if data_df.limit(1).collect().is_empty():
                logger.warning(f"Downloaded data is empty for URL: {self.source_url[key]}. Will mark as failure, be noted.")
                failed_downloads += 1
                continue

            # Remove any leading or trailing whitespaces:
            data_df = data_df.rename(str.strip)

            # __downloaded_data contains the path to the downloaded data if go_through_all_stations is False
            if not self.go_through_all_stations:
                self._EtlPipeline__downloaded_data[key] = data_df
            else:
                if not self._EtlPipeline__downloaded_data:
                    self._EtlPipeline__downloaded_data["station_data"] = data_df
                else:
                    self._EtlPipeline__downloaded_data["station_data"] = pl.concat([self._EtlPipeline__downloaded_data["station_data"], data_df])

        # Check if the number of failed downloads is greater than 50% of the total number of downloads if it is, the warnings are promoted to errors
        if failed_downloads/len(self.source_url.keys()) > FAIL_RATIO:
            logger.error(f"More than 50% of the data was not downloaded, exiting")
            raise RuntimeError(f"More than 50% of the data was not downloaded. {failed_downloads} out of {len(self.source_url.keys())} failed to download. for {self.name} pipeline")

        logger.info(f"Download Complete. Downloaded Data for {len(self.source_url.keys()) - failed_downloads} out of {len(self.source_url.keys())} sources")

    def _load_data_into_tables(self, insert_tablename=None, data=pl.DataFrame(), pkey=None):
        """
        Class instance function that inserts the scraped data into the database. Checks have been put into place as well to ensure that
        there is some data that is trying to be inserted. If there is not, it will raise an Error.

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
            insert_query = f"INSERT INTO {insert_tablename} ({', '.join(df_schema)}) VALUES %s ON CONFLICT ({', '.join(pkey)}) DO UPDATE SET value = EXCLUDED.value;"

            cursor = self.db_conn.cursor()

            logger.debug(f'Inserting {len(records)} rows into the table {insert_tablename}')
            execute_values(cursor, insert_query, records, page_size=100000)

            self.db_conn.commit()

            cursor.close()
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Inserting into the table {insert_tablename} failed!")
            raise RuntimeError(f"Inserting into the table {insert_tablename} failed! Error: {e}")

    def __make_polars_lazyframe(self, response, key):
        """
        Private method to check the following:
            - Scraper needs to gather all stations, and they all have the same data schema
            - Scraper has a data schema that cannot be overriden, happens if the data is too long
            - Scraper has a data schema that can be overriden, and does not have to go through each station to download all files.

        Args:
            response (request.get response): Get Request object that contains the data that will be transformed into a lazyframe.
            key (string): Dictionary key that will make sure that the correct dtype schema is used.

        Output:
            data_df (pl.LazyFrame): Polars LazyFrame object with the retrieved data.
        """
        # This is to collect all the stations data in to one LazyFrame. All stations should have the same schema
        if self.go_through_all_stations:
            data_df = pl.scan_csv(response.raw, has_header=True, schema_overrides=self.expected_dtype["station_data"])

        # This is to load data in to a LazyFrame if the schema is hard to define or too long to override, then use this loader
        elif not self.overideable_dtype:
            data_df = pl.scan_csv(response.raw, has_header=True, infer_schema=True, infer_schema_length=250)

        # This is for all other dataframe loaders. Used when there are multiple files with different dtype schemas being downloaded.
        # The encoding="utf8-lossy" option is selected because one of the sources may have an invalid utf-8 character. This will not affect any sources that only have valid utf-8 characters.
        else:
            data_df = pl.scan_csv(response.raw, has_header=True, schema_overrides=self.expected_dtype[key], encoding="utf8-lossy")

        return data_df

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

        query = f"""
            SELECT
                DISTINCT ON (station_id)
                CASE
                    WHEN network_id IN (3, 50)
                        THEN ltrim(original_id, 'HRB')
                    ELSE original_id
                END AS original_id,
                station_id
            FROM
                bcwat_obs.scrape_station
            JOIN
                bcwat_obs.station_network_id
            USING
                (station_id)
            WHERE
                station_data_source = '{self.station_source}';
        """

        self.station_list = pl.read_database(query=query, connection=self.db_conn, schema_overrides={"original_id": pl.String, "station_id": pl.Int64}).lazy()

    def get_no_scrape_list(self):
        """
        Function that is the counter part of get_station_list. get_station_list only gets the list of stations that are in the database which are supposed to be scraped. There are some stations in the DB that is not supposed to be scraped. Thus, when a new station is found, it is possible that the station is not in the station_list because it is not supposed to be scraped. This function gets the list of stations that are not supposed to be scraped.

        Args:
            None

        Output:
            None
        """
        logger.debug(f"Gathering stations that have the scrape flag as False for the network {self.network}")

        query = f"""
            SELECT
                DISTINCT ON (original_id)
                CASE
                    WHEN network_id IN (3, 50)
                        THEN ltrim(original_id, 'HRB')
                    ELSE original_id
                END AS original_id,
                station_id
            FROM
                bcwat_obs.station
            JOIN
                bcwat_obs.station_network_id
            USING
                (station_id)
            WHERE
                network_id IN ({', '.join(self.network)})
            AND
                scrape = False;
        """

        self.no_scrape_list = pl.read_database(query=query, connection=self.db_conn, schema_overrides={"original_id": pl.String, "station_id": pl.Int64}).lazy()

    def check_for_new_stations(self, external_data = {"station_data":pl.LazyFrame([])}):
        """
        This is a method that will check if there are new stations in the data that was downloaded. It will be compared with the stations that are in the station_list attribute, as well as the
        output of the get_no_scrape_list method.

        Args:
            external_data (dict): Dictionary consisting of Polars LazyFrame object with Station metadata for all stations. If this is None, then it will try to find the new_station data from the
            __downloaded_data attribute.

        Output:
            None
        """

        logger.info(f"Checking for new stations in {self.name} pipeline")
        if external_data["station_data"].limit(1).collect().is_empty():
            downloaded_data = self.get_downloaded_data()
        else:
            downloaded_data = external_data

        self.get_no_scrape_list()

        all_data = pl.LazyFrame([])
        for key in downloaded_data.keys():
            if all_data.limit(1).collect().is_empty():
                all_data = downloaded_data[key].rename(self.column_rename_dict)
            else:
                all_data = pl.concat([all_data, downloaded_data[key].rename(self.column_rename_dict)])

        # Check if station is already part of a different network
        other_network_stations = (
            pl.read_database(query=f"SELECT DISTINCT ON (original_id, station_id) original_id, station_id FROM bcwat_obs.station JOIN bcwat_obs.station_network_id USING (station_id) WHERE network_id NOT IN ({', '.join(self.network)})", connection=self.db_conn)
            .lazy()
        )

        # Remove prefix if it's FlowWorks
        # The cast is just in case that the no_scrape_list is empty. If th

        new_station = (
            all_data
            .join(self.station_list, on="original_id", how="anti")
            .join(self.no_scrape_list.select(pl.col("original_id").cast(pl.String)), on=["original_id"], how="anti")
            .with_columns(
                original_id = pl.when(self.station_source == "flowworks")
                    .then('HRB' + pl.col("original_id"))
                    .otherwise(pl.col("original_id"))
            )
            .join(other_network_stations, on="original_id", how="left")
            .select("original_id", "station_id")
            .unique()
        )

        return new_station

    def check_new_station_in_bc(self, station_df):
        """
        Method that will check if the stations that were passed in are within the BC boundary. If they are not, then they will be returned with a False value.
        If they are False, then they will not be inserted in to the database.

        Args:
            station_df (polars.LazyFrame): Polars LazyFrame object with the station's original_id, longitude, and latitude. Note here that the ORDER OF LAT AND LON MATTER

        Output:
            in_bc_list (list): List of original_ids that are in BC.
        """

        logger.debug("Checking if the new stations that were found are within BC.")

        query = """SELECT %s AS original_id, ST_Within(ST_Point(%s, %s, 4326), geom4326) AS in_bc FROM bcwat_obs.bc_boundary;"""

        cursor = self.db_conn.cursor()

        in_bc_list = []
        for tup in station_df.collect().rows():
            cursor.execute(query, tup)

            result = cursor.fetchall()[0]
            if result[1]:
                in_bc_list.append(result[0])

        return in_bc_list

    def insert_only_station_network_id(self, station_network_id):
        """
        There are cases where a station is already in the database, but for a different network_id. This method will insert the new station network_id in to that table so that it will not be
        considered a new station next time.

        Args:
            station_network_id (pl.DataFrame): A dataframe that consists of the station_id and network_id of stations that already exist in the database but with a different network_id
                Columns:
                    - station_id
                    - network_id

        Output:
            None
        """
        logger.info(f"Inserting {station_network_id.collect().shape[0]} stations with network ids {', '.join(self.network)} to the station_network_id table.")

        cursor = self.db_conn.cursor()

        # Create network_id column with each network_id used in this scraper
        station_network_id = (
            station_network_id
            .with_columns(network_id = self.network)
            .explode("network_id")
            ).collect()

        rows = station_network_id.rows()

        query = f"INSERT INTO bcwat_obs.station_network_id (station_id, network_id) VALUES %s ON CONFLICT (station_id, network_id) DO NOTHING;"

        try:
            execute_values(cursor, query, rows)
        except Exception as e:
            self.db_conn.rollback()
            cursor.close()
            raise(e)

        self.db_conn.commit()
        cursor.close()


    def construct_insert_tables(self, station_metadata):
        """
        This method will construct the dataframes that consists of the metadata required to insert new stations into the database.

        Args:
            station_metadata (polars.DataFrame): Polars DataFrame object with the metadata required for each station. Columns include:
                **FILL COLUMNS**

        Output:
            new_stations (polars.DataFrame): Polars DataFrame object the new sation data for the station table.
            new_station_insert_dict (dict): Dictionary that contains the data required to insert into the following tables:
                - station_project_id
                - station_variable
                - station_year
                - station_type_id
                - station_network_id
        """

        new_station_insert_dict = NEW_STATION_INSERT_DICT_TEMPLATE.copy()

        try:
            # Collect the new station data to be inserted in to station table
            new_stations = (
                station_metadata
                .select(
                    "original_id",
                    "station_name",
                    "station_status_id",
                    "longitude",
                    "latitude",
                    "scrape",
                    "stream_name",
                    "station_description",
                    "operation_id",
                    "drainage_area",
                    "regulated",
                    "user_flag"
                )
                .unique()
            ).collect()

            for key in new_station_insert_dict.keys():
                data_df =(
                    station_metadata
                    .filter(pl.col(new_station_insert_dict[key][0]).is_not_null())
                    .select(
                        pl.col("original_id"),
                        pl.col(new_station_insert_dict[key][0]).cast(pl.List(pl.Int32))
                    )
                    .unique()
                    .explode(new_station_insert_dict[key][0])
                ).collect()

                new_station_insert_dict[key].append(data_df)

        except Exception as e:
            logger.error(f"Error when trying to construct the insert dataframes. Will continue without inserting new stations. Error {e}")
            raise RuntimeError(e)

        return new_stations, new_station_insert_dict

    def insert_new_stations(self, new_stations, metadata_dict):
        """
        If a new station is found, there are some metadata that needs to be inserted in other tables. This function is the collection of all insertions that should happen when new stations are found that are not yet in the DB. After the insertion, an email will be sent to the data team to notify them of the new data, and request a review of the data.

        Args:
            new_stations (polars.DataFrame): Polars DataFrame object with the the following columns:
            Required
                original_id: string
                station_name: string
                station_status_id: integer
                longitude: float
                latitude: float
                scrape: boolean
            Optional:
                stream_name: string
                station_description: string
                operation_id: integer
                geom4326: geometry
                drainage_area: float
                regulated: boolean
                user_flag: boolean

            station_project (polars.DataFrame): Polars DataFrame object with the the following columns:
            Required
                original_id: string
                project_id: integer

            station_variable (polars.DataFrame): Polars DataFrame object with the the following columns:
            Required
                original_id: string
                variable_id: integer

            station_year (polars.DataFrame): Polars DataFrame object with the the following columns:
            Required
                original_id: string
                year: integer

            station_type_id (polars.DataFrame): Polars DataFrame object with the the following columns:
            Required
                original_id: string
                type_id: integer

        Output:
            None
        """
        try:
            logger.debug("Inserting new stations to station table")
            columns = new_stations.columns
            rows = new_stations.rows()
            query = f"""INSERT INTO bcwat_obs.station({', '.join(columns)}) VALUES %s;"""

            cursor = self.db_conn.cursor()

            execute_values(cursor, query, rows, page_size=100000)

        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error when inserting new stations, error: {e}")
            raise RuntimeError(f"Error when inserting new stations, error: {e}")

        logger.debug("Getting new updated station_list")

        # After inserting the new station, the station_list needs to be updated
        self.get_station_list()
        self.get_no_scrape_list()

        # Get station_ids of stations that were just inserted
        try:

            ids = new_stations.get_column("original_id").to_list()
            id_list = ", ".join(f"'{id}'" for id in ids)

            query = f"""
                SELECT original_id, station_id
                FROM bcwat_obs.station
                WHERE original_id IN ({id_list});
            """

            new_station_ids = pl.read_database(query, connection=self.db_conn, schema_overrides={"original_id": pl.String, "station_id": pl.Int64}).lazy()

            # If the scraper is FlowWorks, the "HRB" prefix needs to be removed
            if self.station_source == 'flowworks':
                new_station_ids = (
                    new_station_ids
                    .with_columns(
                        original_id = pl.col("original_id").str.replace("HRB", "")
                    )
                )
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error when getting id's for the new stations that were inserted")
            raise RuntimeError(e)

        complete_station_list = pl.concat([self.station_list, self.no_scrape_list, new_station_ids]).collect()

        cursor = self.db_conn.cursor()

        for key in metadata_dict.keys():
            try:
                logger.debug(f"Inserting station information in to {key} table.")
                # Joining the new stations with the station_list to get the new station_id
                metadata_df = metadata_dict[key][1].join(complete_station_list, on="original_id", how="inner").select("station_id", metadata_dict[key][0])
                columns = metadata_df.columns
                rows = metadata_df.rows()

                query = f"""INSERT INTO {key}({', '.join(columns)}) VALUES %s;"""

                execute_values(cursor, query, rows, page_size=100000)

            except Exception as e:
                self.db_conn.rollback()
                logger.error(f"Error when inserting new {key} rows, error: {e}")
                raise RuntimeError(f"Error when inserting new {key} rows, error: {e}")

        # Only commit if everything succeeded
        self.db_conn.commit()

        logger.debug("New stations have been inserted into the database.")

    def check_year_in_station_year(self):
        """
            This is a method to check that the bcwat_obs.station_year table is up to date with all the years that the data exists for stations.
            This is done by gathering the stations that had data inserted in the scraper run, and checking if the current year is in the station_year table.

            Args:
                None

            Output:
                None
        """
        logger.info("Post Processing: Checking if the station_year table is up to date.")
        station_data = self._EtlPipeline__transformed_data

        station = pl.DataFrame()
        # Get all station_id that have new data inserted into it.
        for key in station_data.keys():
            if not station.is_empty():
                station = pl.concat([station, station_data[key][0].select("station_id").unique()])
            else:
                station = station_data[key][0].select("station_id").unique()

        # Drop duplicate rows and add column year with current year
        station =(
            station
            .unique()
            .with_columns(
                year = self.date_now.year
            )
        )

        cursor = self.db_conn.cursor(cursor_factory = RealDictCursor)

        query = f"""SELECT station_id FROM bcwat_obs.station_year WHERE year = {self.date_now.year};"""

        cursor.execute(query)
        in_db = pl.DataFrame(cursor.fetchall())

        not_in_db = station.join(in_db, on="station_id", how="anti")

        if not_in_db.is_empty():
            logger.info("All years are in the station_year table.")
        else:
            try:
                logger.info(f"Found some stations that did not have the current year in the table. Inserting {not_in_db.shape[0]} rows.")
                insert_query = """INSERT INTO bcwat_obs.station_year (station_id, year) VALUES %s;"""
                execute_values(cursor, insert_query, not_in_db.rows(), page_size=100000)
                self.db_conn.commit()
            except Exception as e:
                raise RuntimeError(f"Error when inserting new station_year rows, error: {e}")

    def check_number_of_stations_scraped(self):
        """
        Method to check the number of stations scraped in relation to the total number of stations that this scraper should scrape.
        If the ratio of stations scraped is below the minimum acceptability ratio, an email will be sent to the data team as a warning.
        The minimum acceptability ratio is defined in the constant file and is specific to each scraper.

        Args:
            None

        Output:
            None
        """
        logger.info("Checking if the number of stations scraped is acceptable.")
        transformed_data = self._EtlPipeline__transformed_data
        total_scrape_station_count = self.station_list.collect().shape[0]

        station_count_with_data = []
        # Get number of unique station_ids in each dataframe in dictionary
        for key in transformed_data:
            ratio = transformed_data[key][0].select("station_id").unique().shape[0]/total_scrape_station_count
            station_count_with_data.append({
                "key": key,
                "station_ratio": ratio,
                "is_acceptable": ratio >= self.min_ratio[key]
            })

        ratio_frame = pl.DataFrame(station_count_with_data)

        if not ratio_frame.filter(~pl.col("is_acceptable")).is_empty():
            logger.warning(f"The ratio of unique station_ids in the transformed data to total stations scraped does not meet the acceptability criteria, sending email and continuing: {ratio_frame.filter(~pl.col('is_acceptable')).rows()}")

            # TODO Email warning that the ratio does not meet acceptability
        else:
            logger.info("The stations scraped for all tables meets the acceptability criteria!")
