from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    WEATHER_FARM_PRD_BASE_URL,
    WEATHER_FARM_PRD_DESTINATION_TABLES,
    WEATHER_FARM_PRD_DTYPE_SCHEMA,
    WEATHER_FARM_PRD_NAME,
    WEATHER_FARM_PRD_NETWORK_ID,
    WEATHER_FARM_PRD_RENAME_DICT,
    WEATHER_FARM_PRD_STATION_SOURCE
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class WeatherFarmPrdPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=WEATHER_FARM_PRD_NAME,
            source_url=[],
            destination_tables=WEATHER_FARM_PRD_DESTINATION_TABLES,
            days=3,
            station_source=WEATHER_FARM_PRD_STATION_SOURCE,
            expected_dtype=WEATHER_FARM_PRD_DTYPE_SCHEMA,
            column_rename_dict=WEATHER_FARM_PRD_RENAME_DICT,
            go_through_all_stations=True,
            overrideable_dtype=True,
            network_ids= WEATHER_FARM_PRD_NETWORK_ID,
            db_conn=db_conn,
            date_now=date_now
        )

        ## Add Implementation Specific attributes below
        self.station_source = 'temp'

    def get_station_list(self):
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



    def transform_data(self):
        pass

    def validate_downloaded_data(self):
        pass

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def __implementation_specific_private_func(self):
        pass
