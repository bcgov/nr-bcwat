from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.functions import setup_logging
import requests
import polars as pl
import os
import pendulum
from bs4 import BeautifulSoup

logger = setup_logging()

class HydatPipeline(StationObservationPipeline):
    def __init__(self):
        super().__init__(name="Quarterly Hydat", source_url='tempurl', destination_tables=["temp"])

        ## Add Implementation Specific attributes below
        self.station_source = 'temp'

    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def __check_for_new_hydat(self):
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
        url_date = pendulum.strptime(
            url_time, "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/Hydat_sqlite3_%Y%m%d.zip"
        ).date()

        logger.info("Newest version of hydat available: %s" % str(url_date))

        cur = self.db_conn.cursor()

        query = """
            SELECT data_date FROM wet.import_date WHERE dataset='hydat';
        """
        cur.execute(query)
        result = cur.fetchall()

        logger.info(f"Current Version of hydat in db: {result[0][0]}")
        if len(result) == 0 or result[0][0] is None:
            return url_date, full_url
        elif url_date > result[0][0]:
            return url_date, full_url
        else:
            return None, None
