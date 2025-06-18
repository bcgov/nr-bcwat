from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    QUARTERLY_HYDAT_NAME,
    QUARTERLY_HYDAT_BASE_URL,
    QUARTERLY_HYDAT_MIN_RATIO,
    QUARTERLY_HYDAT_STATION_SOURCE,
    QUARTERLY_HYDATE_NETWORK_ID,
    QUARTERLY_HYDAT_DESTINATION_TABLES,
    QUARTERLY_HYDAT_DTYPE_SCHEMA,
    QUARTERLY_HYDAT_RENAME_DICT,
    QUARTERLY_HYDAT_DISCHARGE_QUERY,
    QUARTERLY_HYDATE_LEVEL_QUERY,
    HEADER,
    MAX_NUM_RETRY
)
from etl_pipelines.utils.functions import setup_logging
import requests
import polars as pl
import polars.selectors as cs
import os
import pendulum
import zipfile
from bs4 import BeautifulSoup
from time import sleep
import psutil
import sqlalchemy 

process = psutil.Process()


logger = setup_logging()

class HydatPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=QUARTERLY_HYDAT_NAME,
            source_url='',
            destination_tables=QUARTERLY_HYDAT_DESTINATION_TABLES,
            days=2,
            station_source=QUARTERLY_HYDAT_STATION_SOURCE,
            expected_dtype=QUARTERLY_HYDAT_DTYPE_SCHEMA,
            column_rename_dict=QUARTERLY_HYDAT_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=False,
            network_ids=QUARTERLY_HYDATE_NETWORK_ID,
            min_ratio=QUARTERLY_HYDAT_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )
        # Please change this to false before PR
        self.will_import = True

        # This is a temporary path so that I can test locally. Once I know how to use persistent volumes please change to that path.
        self.file_path = "airflow/temp/"
        self.sqlite_path = 'airflow/temp/Hydat.sqlite3'

        self.__check_for_new_hydat()

    def download_data(self):
        logger.info(f"Downloading Zipped Hydat from {self.source_url}")

        while True:
            try:
                response = requests.get(self.source_url, stream=True, headers=HEADER, timeout=20)
            except Exception as e:
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Error downloading Hydat from URL: {self.source_url}. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(5)
                    continue
                else:
                    logger.error(f"Failed to download Hydat from {self.source_url}. Raising Error {e}", exc_info=True)
                    raise RuntimeError(f"Failed to download Hydat from {self.source_url}. Error {e}")

            if response.status_code != 200:
                if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Response status was not 200. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(5)
                    continue
                else:
                    logger.error(f"Response status was not 200 when trying to download Hydat. Raising Error {e}", exc_info=True)
                    raise RuntimeError(f"Response status was not 200 when trying to download Hydat. Error {e}")
            break

        # Used to prevent loading the response to memory all at once.
        try:
            with open(os.path.join(self.file_path, self.source_url.split("/")[-1]), "wb") as f:
                for chunk in response.iter_content(chunk_size=1024*2048):
                    if chunk:
                        f.write(chunk)
        except Exception as e:
            logger.error(f"Failed when trying to write the chunked zipped Hydat file to disk. Error {e}", exc_info=True)
            raise IOError(f"Failed when trying to write the chunked zipped Hydat file to disk. Error {e}")

        logger.info(f"Finished downloading Hydat, Unzipping the Zip file")

        try:
            with zipfile.ZipFile(os.path.join(self.file_path, self.source_url.split("/")[-1]), "r") as zip_ref:
                zip_ref.extractall(self.file_path)
        except Exception as e:
            logger.error(f"Failed when trying to unzip the Hydat file. Error {e}", exc_info=True)
            raise IOError(f"Failed when trying to unzip the Hydat file. Error {e}")

        logger.info(f"Finished Unzipping Hydat")

    def extract_data(self):
        logger.info("Extracting data from the Hydat.sqlite3 database file")

        hydat_conn = f"sqlite://{self.sqlite_path}"

        logger.info("Dropping the table bcwat_obs.hydat_discharge_level_data if it already exists and recreating the table.")
        # Temporary table to store the large discharge and level data into. Will be dropped by the end of the script.
        cursor = self.db_conn.cursor()
        query = """
            DROP TABLE IF EXISTS bcwat_obs.hydat_discharge_level_data;
            CREATE TABLE bcwat_obs.hydat_discharge_level_data(
                STATION_NUMBER text,
                variable_id smallint,
                date date,
                val double precision,
                symbol text
            );
        """
        cursor.execute(query)

        try:
            logger.info("Loading Flow Data into the database table bcwat_obs.hydat_discharge_level_data")
            # This is done instead of storing in memory because the transformation changes it into a very large dataframe.
            self.__load_into_hydat_discharge_level_data_incrementally(
                query=QUARTERLY_HYDAT_DISCHARGE_QUERY,
                var_type="FLOW"
            )
        except Exception as e:
            logger.error(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database, and insert it into the table bcwat_obs.hydat_discharge_level_data. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database, and insert it into the table bcwat_obs.hydat_discharge_level_data. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            logger.info("Loading Level Data into the database table bcwat_obs.hydat_discharge_level_data")
            # This is done instead of storing in memory because the transformation changes it into a very large dataframe.
            self.__load_into_hydat_discharge_level_data_incrementally(
                query=QUARTERLY_HYDATE_LEVEL_QUERY,
                var_type="LEVEL"
            )
        except Exception as e:
            logger.error(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database, and insert it into the table bcwat_obs.hydat_discharge_level_data. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database, and insert it into the table bcwat_obs.hydat_discharge_level_data. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            self._EtlPipeline__downloaded_data = {"station": self.__read_sqlite_database(query="select station_number, station_name, prov_terr_state_loc, regional_office_id, hyd_status, sed_status, latitude, longitude, drainage_area_gross, drainage_area_effect, cast(rhbn as text) as rhbn, cast(real_time as text) as real_time, contributor_id, operator_id, datum_id from STATIONS")}

        except Exception as e:
            logger.error(f"Failed to extract data from STATIONS table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from STATIONS table from Hydat.sqlite3 database. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            self._EtlPipeline__downloaded_data = {"operation_codes": self.__read_sqlite_database(query="select * from OPERATION_CODES")}
        except Exception as e:
            logger.error(f"Failed to extract data from OPERATION_CODES table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from OPERATION_CODES table from Hydat.sqlite3 database. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            self._EtlPipeline__downloaded_data = self.__read_sqlite_database(query="select * from AGENCY_LIST")
        except Exception as e:
            logger.error(f"Failed to extract data from AGENCY_LIST table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from AGENCY_LIST table from Hydat.sqlite3 database. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            self._EtlPipeline__downloaded_data = {"data_symbols": self.__read_sqlite_database(query="select * from DATA_SYMBOLS")}
        except Exception as e:
            logger.error(f"Failed to extract data from DATA_SYMBOLS table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from DATA_SYMBOLS table from Hydat.sqlite3 database. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            self._EtlPipeline__downloaded_data = {"stn_data_collection": self.__read_sqlite_database(query="select * from STN_DATA_COLLECTION")}
        except Exception as e:
            logger.error(f"Failed to extract data from STN_DATA_COLLECTION table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from STN_DATA_COLLECTION table from Hydat.sqlite3 database. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            self._EtlPipeline__downloaded_data = {"stn_regulation": self.__read_sqlite_database(query="select * from STN_REGULATION")}
        except Exception as e:
            logger.error(f"Failed to extract data from STN_REGULATION table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from STN_REGULATION table from Hydat.sqlite3 database. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        logger.info(f"Finished extracting the necessary data from Hydat.sqlite3.")


    def transform_data(self):
        logger.info(f"Starting Transfromation step for {self.name}")

        data = self.get_downloaded_data()

        station_query = """
            SELECT * FROM bcwat_obs.station
            JOIN bcwat_obs.station_network_id
            ON (station_id)
            WHERE network_id = 1
            OR original_id IN ('09AA010','08NE010','08NH006','08NE058','09AA014','08NN012','08NH021','09AE004','08NP001','09AA015')
        """

        bcwat_obs_stations = pl.read_database(
            query=station_query,
            connection=self.db_conn
        ).lazy()




        logger.info(f"Finished Transformation step for {self.name}")
        pass

    def validate_downloaded_data(self):
        pass

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def __check_for_new_hydat(self):
        """
        This function checks if there is a newer version of hydat available online than currently in the database.
        If so, it returns the date of the new version and a url to download it.
        If not, it returns None, None.

        Args:
            None

        Output:
            None or url_date (datetime): The date of the newest version of hydat available online.
            None or full_url (str): The url to download the newest version of hydat.
        """
        url = "http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/"
        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, features="lxml")

        for a in soup.find_all("a", href=True):
            if a["href"].find("sqlite3") != -1:
                full_url = os.path.join(url, a["href"])
            else:
                continue

        r = requests.head(full_url)
        url_time = r.headers["Location"]
        url_date = pendulum.from_format(
            url_time[-12:-4], "YYYYMMDD"
        ).date()

        logger.info("Newest version of hydat available: %s" % str(url_date))

        cur = self.db_conn.cursor()

        query = """
            SELECT import_date FROM bcwat_lic.bc_data_import_date WHERE dataset='hydat';
        """
        cur.execute(query)
        result = cur.fetchall()
        cur.close()

        logger.info(f"Current Version of hydat in db: {result[0][0]}")
        self.source_url = full_url
        if ((len(result) == 0) or (result[0][0] is None) or (url_date > result[0][0])):
            self.will_import = True

    def __read_sqlite_database(self, query=None):
        if not query:
            logger.error(f"Empty query has been passed in! Please ensure that you are using this method properly!")
            raise ValueError(f"Empty query has been passed in! Please ensure that you are using this method properly!")

        hydat_conn = "sqlite://" + self.sqlite_path

        return pl.read_database_uri(query=query, uri=hydat_conn).lazy()


    def __load_into_hydat_discharge_level_data_incrementally(self, query, var_type):
        hydat_conn = sqlalchemy.create_engine("sqlite://"+self.sqlite_path, echo=True).connect()
        # Try this SQLAlchemy method, if it doesn't work so well, try the pl.read_database() method with iter_batch=True, and batch_size = 1000000
        with hydat_conn.execution_options(yield_per=1000000).execute(QUARTERLY_HYDAT_DISCHARGE_QUERY) as result:
            for chunk in result.partition():
                df = (
                    pl.LazyFrame(chunk)
                    .unpivot(
                        index=["STATION_NUMBER", "YEAR", "MONTH"], 
                        on=cs.matches(f"^{var_type}\\d+$"), 
                        variable_name="Day", 
                        value_name="val"
                    )
                    .drop_nulls("val")
                    .with_columns(
                        pl.col("Day").str.extract(r"(\d+)", 1).cast(pl.Int32)
                    )
                    .join(
                        other=(
                            pl.LazyFrame(chunk)
                            .unpivot(
                                index=["STATION_NUMBER", "YEAR", "MONTH"],
                                on=cs.matches(f"^{var_type}_SYMBOL\\d+$"), 
                                variable_name="Day", 
                                value_name="symbol"
                            )
                        ),
                        on=["STATION_NUMBER", "YEAR", "MONTH", "Day"],
                        how="inner",
                        suffix=""
                    )
                    .with_columns(
                        date = pl.date(year=pl.col("YEAR"), month=pl.col("MONTH"), day=pl.col("Day")),
                        variable_id = pl.lit(1)
                    )
                    .drop(["YEAR", "MONTH", "Day"])
                ).collect()

                df.write_database(
                    table_name="bcwat_obs.hydat_discharge_level_data", 
                    connection=self.db_conn
                )
