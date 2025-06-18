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
    HEADER,
    MAX_NUM_RETRY
)
from etl_pipelines.utils.functions import setup_logging
import requests
import polars as pl
import os
import pendulum
import zipfile
from bs4 import BeautifulSoup
from time import sleep
import psutil

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

        try:
            self._EtlPipeline__downloaded_data = {"dly_flows": self.__read_sqlite_database(query="""select "STATION_NUMBER","YEAR","MONTH","FLOW1","FLOW_SYMBOL1","FLOW2","FLOW_SYMBOL2","FLOW3","FLOW_SYMBOL3","FLOW4","FLOW_SYMBOL4","FLOW5","FLOW_SYMBOL5","FLOW6","FLOW_SYMBOL6","FLOW7","FLOW_SYMBOL7","FLOW8","FLOW_SYMBOL8","FLOW9","FLOW_SYMBOL9","FLOW10","FLOW_SYMBOL10","FLOW11","FLOW_SYMBOL11","FLOW12","FLOW_SYMBOL12","FLOW13","FLOW_SYMBOL13","FLOW14","FLOW_SYMBOL14","FLOW15","FLOW_SYMBOL15","FLOW16","FLOW_SYMBOL16","FLOW17","FLOW_SYMBOL17","FLOW18","FLOW_SYMBOL18","FLOW19","FLOW_SYMBOL19","FLOW20","FLOW_SYMBOL20","FLOW21","FLOW_SYMBOL21","FLOW22","FLOW_SYMBOL22","FLOW23","FLOW_SYMBOL23","FLOW24","FLOW_SYMBOL24","FLOW25","FLOW_SYMBOL25","FLOW26","FLOW_SYMBOL26","FLOW27","FLOW_SYMBOL27","FLOW28","FLOW_SYMBOL28","FLOW29","FLOW_SYMBOL29","FLOW30","FLOW_SYMBOL30","FLOW31","FLOW_SYMBOL31" from DLY_FLOWS""")}
        except Exception as e:
            logger.error(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database. Error {e}")
        logger.info(f"Memory usage is at: {process.memory_info().rss/ 1024 ** 2} MiB. Please keep an eye on me" )

        try:
            self._EtlPipeline__downloaded_data = {"dly_flows": self.__read_sqlite_database(query="""select "STATION_NUMBER","YEAR","MONTH","LEVEL1","LEVEL_SYMBOL1","LEVEL2","LEVEL_SYMBOL2","LEVEL3","LEVEL_SYMBOL3","LEVEL4","LEVEL_SYMBOL4","LEVEL5","LEVEL_SYMBOL5","LEVEL6","LEVEL_SYMBOL6","LEVEL7","LEVEL_SYMBOL7","LEVEL8","LEVEL_SYMBOL8","LEVEL9","LEVEL_SYMBOL9","LEVEL10","LEVEL_SYMBOL10","LEVEL11","LEVEL_SYMBOL11","LEVEL12","LEVEL_SYMBOL12","LEVEL13","LEVEL_SYMBOL13","LEVEL14","LEVEL_SYMBOL14","LEVEL15","LEVEL_SYMBOL15","LEVEL16","LEVEL_SYMBOL16","LEVEL17","LEVEL_SYMBOL17","LEVEL18","LEVEL_SYMBOL18","LEVEL19","LEVEL_SYMBOL19","LEVEL20","LEVEL_SYMBOL20","LEVEL21","LEVEL_SYMBOL21","LEVEL22","LEVEL_SYMBOL22","LEVEL23","LEVEL_SYMBOL23","LEVEL24","LEVEL_SYMBOL24","LEVEL25","LEVEL_SYMBOL25","LEVEL26","LEVEL_SYMBOL26","LEVEL27","LEVEL_SYMBOL27","LEVEL28","LEVEL_SYMBOL28","LEVEL29","LEVEL_SYMBOL29","LEVEL30","LEVEL_SYMBOL30","LEVEL31","LEVEL_SYMBOL31" from DLY_LEVELS""")}
        except Exception as e:
            logger.error(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database. Error {e}", exc_info=True)
            raise IOError(f"Failed to extract data from DLY_FLOWS table from Hydat.sqlite3 database. Error {e}")
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


    def transform_data(self):
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

    def __extract_and_load_discharge_and_level_data(self):
        pass
