from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    WEATHER_FARM_PRD_BASE_URL,
    WEATHER_FARM_PRD_DESTINATION_TABLES,
    WEATHER_FARM_PRD_DTYPE_SCHEMA,
    WEATHER_FARM_PRD_NAME,
    WEATHER_FARM_PRD_NETWORK_ID,
    WEATHER_FARM_PRD_RENAME_DICT,
    WEATHER_FARM_PRD_STATION_SOURCE,
    WEATHER_FARM_PRD_MIN_RATIO
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl
import json

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
            min_ratio=WEATHER_FARM_PRD_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )

        ## Add Implementation Specific attributes below
        # The old scrapers had it scraping a whole day ahead as well. I assume this is so that it captures all data that is available.
        self.end_date = self.end_date.add(days=1)

        self.source_url = {station_id[0]: WEATHER_FARM_PRD_BASE_URL.format(self.start_date.to_date_string(), self.end_date.to_date_string(), station_id[2]) for station_id in self.station_list.collect().rows()}



    def get_station_list(self):
        """
        Weather Farm PRD scraper implementation of get_station_list(). Gets the list of station_id to scrape from the database. Along with it, it gets the original_id of the stations, and an unique_id which is used as the original_id when we request a specific date range of data.

        Args:
            None

        Output:
            None
        """

        logger.debug(f"Gathering Stations from Database using station_source: {self.station_source}")

        query = f"""
            SELECT
                DISTINCT ON (station_id)
                original_id,
                station_id,
                import_json->>'StationId' as unique_id
            FROM
                bcwat_obs.scrape_station
            JOIN
                bcwat_obs.station_network_id
            USING
                (station_id)
            JOIN
                bcwat_obs.station
            USING
                (station_id, original_id)
            WHERE
                station_data_source = '{self.station_source}';
        """

        self.station_list = pl.read_database(query=query, connection=self.db_conn, schema_overrides={"original_id": pl.String, "station_id": pl.Int64, "unique_id": pl.String}).lazy()

    def _StationObservationPipeline__make_polars_lazyframe(self, response, key=None):

        """
        Weather Farm PRD implementation of the __make_polars_lazyframe method.

        This method processes the JSON response from a request, converting it into a lazy-loaded
        Polars DataFrame. It handles missing values by using the coalesce function to replace
        them with default values and casts columns to their appropriate data types.
        If the response contains an empty list, it raises a ValueError.

        Args:
            response (requests.Response): The response object containing JSON data from the request.
            key (string): A key used to label the data with an original_id.

        Output:
            data_df (pl.LazyFrame): A Polars LazyFrame containing the processed data.
        """
        # Haven't happened yet but figured it would be safer to check just incase.
        if response.text == "[]":
            raise ValueError(f"There is no data in the station. Continuing but marking as failure")

        data_df = (
            pl.LazyFrame([row for row in json.loads(response.text)])
            # For this data source, a lot of the stations do not report all of the variables. So if we tried to concat them all, it would fail due to
            # mismatch of columns. This is solved by coalescing the values if the column exists, and otherwise making a column of that name filled
            # with Null values.
            .with_columns(
                accumPrecip = pl.coalesce(pl.col("^accumPrecip$"), None).cast(pl.Float64),
                ytdPrecip = pl.coalesce(pl.col("^ytdPrecip$"), None).cast(pl.Float64),
                dateTimeStamp = pl.coalesce(pl.col("^dateTimeStamp$"), None).cast(pl.String),
                humidityOut = pl.coalesce(pl.col("^humidityOut$"), None).cast(pl.Int64),
                rainfall = pl.coalesce(pl.col("^rainfall$"), None).cast(pl.Float64),
                tempMax = pl.coalesce(pl.col("^tempMax$"), None).cast(pl.Float64),
                tempMin = pl.coalesce(pl.col("^tempMin$"), None).cast(pl.Float64),
                tempAvg = pl.coalesce(pl.col("^tempAvg$"), None).cast(pl.Float64),
                windChill = pl.coalesce(pl.col("^windChill$"), None).cast(pl.Float64),
                windPrevailDir = pl.coalesce(pl.col("^windPrevailDir$"), None).cast(pl.Int64),
                windspeedAvg = pl.coalesce(pl.col("^windspeedAvg$"), None).cast(pl.Float64),
                windspeedHigh = pl.coalesce(pl.col("^windspeedHigh$"), None).cast(pl.Int64),
                frostFreeDays = pl.coalesce(pl.col("^frostFreeDays$"), None).cast(pl.Int64),
                original_id = pl.lit(key)
            )
            .select(
                # The order of the columns also matter when we concat, so we need to order them in a common order.
                "original_id",
                "dateTimeStamp",
                "accumPrecip",
                "ytdPrecip",
                "rainfall",
                "humidityOut",
                "tempMax",
                "tempMin",
                "tempAvg",
                "windChill",
                "windPrevailDir",
                "windspeedAvg",
                "windspeedHigh",
                "frostFreeDays"
            )
        )

        return data_df

    def transform_data(self):
        logger.info(f"Transforming downloaded data for {self.name}")

        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")

        # TODO: Check for new stations, and insert them into the database if they are new, along with their metadata. Send Email after completion.

        logger.debug(f"Starting Transformation")

        df = downloaded_data["station_data"]

        try:
            df = (
                df
                .rename(self.column_rename_dict)
                # According to the old scrapers this is what the NODATA value is for this source
                .remove((pl.col("tempMax") == -17.8) & (pl.col("tempMin") == -17.8) & (pl.col("rainfall") == 0))
                # A lot of the variables we actually don't even keep
                .drop([
                    "accumPrecip",
                    "ytdPrecip",
                    "humidityOut",
                    "windChill",
                    "windPrevailDir",
                    "windspeedAvg",
                    "windspeedHigh",
                    "frostFreeDays"
                ])
                .unpivot(index=["original_id", "datestamp"])
                .with_columns(
                    qa_id = 1,
                    datestamp = pl.col("datestamp").str.to_date("%FT%T"),
                    variable_id = (pl
                        .when(pl.col("variable") == "tempMax").then(6)
                        .when(pl.col("variable") == "tempAvg").then(7)
                        .when(pl.col("variable") == "tempMin").then(8)
                        .when(pl.col("variable") == "rainfall").then(27)
                    )
                )
                .remove(pl.col("value").is_null())
                .join(self.station_list, on="original_id", how="inner")
                .unique()
                .select(
                    "station_id",
                    "datestamp",
                    "variable_id",
                    "value",
                    "qa_id"
                )
            ).collect()

        except Exception as e:
            logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")

        temp_df = (
            df
            .filter(pl.col("variable_id").is_in([6, 7, 8]))
        )
        rain_df = (
            df
            .filter(pl.col("variable_id") == 27)
        )

        self._EtlPipeline__transformed_data = {
            "temperature": [temp_df, ["station_id", "datestamp", "variable_id"]],
            "rainfall": [rain_df, ["station_id", "datestamp", "variable_id"]]
        }

        logger.info(f"Finished Transformation for {self.name}")

    def get_and_insert_new_stations(self, station_data=None):
        pass
