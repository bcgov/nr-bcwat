from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    DRIVE_BC_DESTINATION_TABLES,
    DRIVE_BC_BASE_URL,
    DRIVE_BC_DTYPE_SCHEMA,
    DRIVE_BC_NAME,
    DRIVE_BC_NETWORK_ID,
    DRIVE_BC_RENAME_DICT,
    DRIVE_BC_STATION_SOURCE,
    DRIVE_BC_MIN_RATIO,
    DRIVE_BC_HOURLY_TO_DAILY,
    STR_DIRECTION_TO_DEGREES
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl
import json

logger = setup_logging()

class DriveBcPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=DRIVE_BC_NAME,
            source_url=DRIVE_BC_BASE_URL,
            destination_tables=DRIVE_BC_DESTINATION_TABLES,
            days=2,
            station_source=DRIVE_BC_STATION_SOURCE,
            expected_dtype=DRIVE_BC_DTYPE_SCHEMA,
            column_rename_dict=DRIVE_BC_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=False,
            network_ids= DRIVE_BC_NETWORK_ID,
            min_ratio=DRIVE_BC_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
            )


    def transform_data(self):
        """
        Transformation function for the drive_bc scraper. Since the all the units are included in the column values, they will be removed in the first with_columns statement. After which, the data will be unpivoted to match the schema of the database tables. The station_id from the database is joined on to the data using the original_id value. In the end, only the columns that match the table in the database are kept.

        This transformation is significantly simpler than the others for the following reasons:
            - This scraper is ran HOURLY, so aggregation to daily values happen only once a day, so little to no transformation is required.
            - All data goes into ONE table, this is because this is the only hourly scraper there is.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Transforming downloaded data for {self.name}")

        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")

        # TODO: Check for new stations, and insert them into the database if they are new, along with their metadata. Send Email after completion.

        logger.debug(f"Starting Transformation")

        df = downloaded_data["drive_bc"]

        try:
            # Unfortunately all the value columns of the data have their units attached to it. So we will have to remove them here
            df = (
                df
                .rename(self.column_rename_dict)
                # Uneeded columns
                .drop("received", "elevation", "event", "dataStatus")
                # Apparently some dates are not recorded correctly, resulting in "" values
                .remove(pl.col("datetimestamp") == pl.lit("No Data Reported"))
                .with_columns(
                    airTemp = pl.col("airTemp").str.replace(" &#176C", ""),
                    windMean = pl.col("windMean").str.replace(" km/h", ""),
                    windMax = pl.col("windMax").str.replace(" km/h", ""),
                    windDir = pl.col("windDir").replace_strict(STR_DIRECTION_TO_DEGREES, default=None),
                    roadTemp = pl.col("roadTemp").str.replace(" &#176C", ""),
                    snowSince = pl.col("snowSince").str.replace(" cm", ""),
                    snowEnd = pl.col("snowEnd").str.replace(" cm", ""),
                    snowDepth = pl.col("snowDepth").str.replace(" cm", ""),
                    precip = pl.col("precip").str.replace(" mm", ""),
                    # Not using Boolean type here since this will be included in the "value" column, which will be casted to pl.Float64 later
                    precipLastHr = pl.when(pl.col("precipLastHr") == pl.lit("Yes"))
                        .then(1)
                        .otherwise(0),
                    # Storing as PDT so that the data can be aggregated in to 24 hours of PDT day
                    datetimestamp = pl.col("datetimestamp").str.slice(offset=0, length=19).str.to_datetime("%Y-%m-%d %H:%M:%S", time_zone="America/Vancouver")
                )
                .unpivot(index=["original_id", "station_name", "datetimestamp", "lat", "lon", "station_description"])
                .remove((pl.col("value") == pl.lit("No Data Reported")) | (pl.col("original_id").is_null()))
                .with_columns(
                    variable_id = (pl
                        .when(pl.col("variable") == pl.lit("snowDepth")).then(5)
                        .when(pl.col("variable") == pl.lit("airTemp")).then(7)
                        .when(pl.col("variable") == pl.lit("windMean")).then(9)
                        .when(pl.col("variable") == pl.lit("windMax")).then(10)
                        .when(pl.col("variable") == pl.lit("windDir")).then(11)
                        .when(pl.col("variable") == pl.lit("roadTemp")).then(12)
                        .when(pl.col("variable") == pl.lit("snowSince")).then(13)
                        .when(pl.col("variable") == pl.lit("snowEnd")).then(14)
                        .when(pl.col("variable") == pl.lit("precipLastHr")).then(15)
                        .when(pl.col("variable") == pl.lit("precip")).then(17)
                        ),
                    qa_id = 0

                )
                .remove(pl.col("value") == pl.lit("No Sensor"))
                .join(self.station_list, on="original_id", how="inner")
                .select(
                    pl.col("station_id"),
                    pl.col("datetimestamp"),
                    pl.col("variable_id"),
                    pl.col("value").cast(pl.Float64),
                    pl.col("qa_id")
                )
            ).collect()
        except Exception as e:
            logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")

        # Set private variable to have the transformed data as well as list of primary keys
        self._EtlPipeline__transformed_data["drive_bc"] = {"df": df, "pkey": ["station_id", "datetimestamp", "variable_id"], "truncate": False}

        logger.info(f"Finished Transforming data for {self.name}")

    def _StationObservationPipeline__make_polars_lazyframe(self, response, key=None):
        """
        This DriveBC's method of loading the retrieved data into a pl.LazyFrame object since the data is a JSON string.

        There are also stations with "" as column values. JSON loads does not play well with that, which confuses the pl.LazyFrame constructor. So replace all instances of "" with "No Data Reported"

        Args:
            response (request.get response): Get Request object that contains the data that will be transformed into a lazyframe.
            key (string): Dictionary key that will make sure that the correct dtype schema is used.

        Output:
            data_df (pl.LazyFrame): Polars LazyFrame object with the retrieved data.
        """
        data_df = pl.LazyFrame([row["station"] for row in json.loads(response.text.replace('""', '"No Data Reported"'))], schema_overrides=self.expected_dtype["drive_bc"])

        return data_df

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def convert_hourly_data_to_daily_data(self):
        """
        This function retrieves hourly climate observation data, converts the timestamps to the 'America/Vancouver' timezone,
        and aggregates the data into daily summaries based on predefined transformations specified in the
        DRIVE_BC_HOURLY_TO_DAILY dictionary. The resulting daily data is stored in self._EtlPipeline__transformed_data
        for each data group defined in the dictionary.

        Args:
            None

        Output:
            None
        """

        logger.info(f"Starting to convert hourly data to daily data for {self.name}")

        query = f"""
            SELECT
                *
            FROM
                bcwat_obs.climate_hourly
            WHERE
                datetimestamp > (current_date::timestamp AT TIME ZONE 'America/Vancouver' - INTERVAL '{self.days + 7} DAYS')
        """

        try:
            logger.debug(f"Getting hourly data from bcwat_obs.climate_hourly")
            hourly_data = pl.read_database(query=query, connection=self.db_conn, infer_schema_length=100).lazy()
        except Exception as e:
            logger.error(f"Failed to get hourly data from bcwat_obs.climate_hourly for {self.name}! Error: {e}")
            raise RuntimeError(f"Failed to get hourly data from bcwat_obs.climate_hourly for {self.name}! Error: {e}")

        try:
            logger.debug(f"Converting hourly data's datetime column to be datetime type instead of string.")
            daily_data = (
                hourly_data
            )

            logger.debug(f"Looping though the DRIVE_BC_HOURLY_TO_DAILY dictionary to convert hourly data to daily data.")
            complete_df_list = []
            for key, value in DRIVE_BC_HOURLY_TO_DAILY.items():
                logger.debug(f"Transforming hourly data to daily data for {key}")

                complete_df_list.append(
                    self.__create_daily_data_dataframe(
                        daily_data,
                        value
                    )
                )

            self._EtlPipeline__transformed_data["station_data"] = {
                "df": pl.concat(complete_df_list),
                "pkey": ["station_id", "datestamp", "variable_id"],
                "truncate": False
            }

        except Exception as e:
            logger.error(f"Failed to convert hourly data to daily data for the group {key}! Error: {e}")
            raise RuntimeError(f"Failed to convert hourly data to daily data for the group {key}! Error: {e}")

        logger.info(f"Finished converting houly data to daily data and inserting into Database.")


    def __create_daily_data_dataframe(self, data, metadata):
        """
        This method filters and processes the input data based on the metadata instructions
        for each key, which define variable IDs, aggregation methods, and time grouping details.
        The processed data is aggregated on a daily basis and returned as a Polars DataFrame.

        Args:
            data (pl.LazyFrame): The input dataset containing hourly observation data.
            metadata (dict): A dictionary where each key maps to a configuration dict that specifies:
                - "var_id" (list): List of variable IDs to filter.
                - "start_hour" (int): Starting hour for daily aggregation.
                - "every_period" (str): The period over which to aggregate data (e.g., '1d' for one day).
                - "offset" (str): Offset for time grouping.
                - "group_by_type" (str): Aggregation method to apply ('sum', 'mean', 'max', 'min').
                - "new_var_id" (int): The variable ID to assign to the aggregated data.

        Output:
            pl.DataFrame: A concatenated DataFrame containing the daily aggregated data for each variable defined in the metadata.
        """

        final_df = []
        for key, value in metadata.items():
            logger.debug(f"Converting {key} hourly data to daily data.")
            try:
                result = (
                    data
                    # Filter down to only times with hour 18 and from daily_snow_amount.
                    .filter(
                        (pl.lit(key) != pl.lit("daily_snow")) |
                        (pl.col("datetimestamp").dt.hour() == pl.lit(18))
                        )
                    .filter(
                        (pl.col("variable_id").is_in(value["var_id"])) &
                        (pl.col("datetimestamp") >= self.date_now.subtract(days=self.days).set(hour=value["start_hour"], minute=0, second=0)) &
                        (pl.col("datetimestamp") < self.date_now.date())
                    )
                    # Some of the variables get combied to be one variable in the end. So removing the var_id is necessary
                    .drop("variable_id")
                    # Sorting by group is required for the group_by_dynamic function.
                    .sort ("station_id", "datetimestamp")
                    # group_by_dynamic allows us to define how far to group by, and how often.
                    .group_by_dynamic(
                        index_column="datetimestamp",
                        every=value["every_period"],
                        period=value["every_period"],
                        offset=value["offset"],
                        label="right",
                        group_by=["station_id", "qa_id"]
                    )
                )

                # Apply different aggregation methods to the data depending on the argument.
                if value["group_by_type"] == "sum":
                    result = result.sum()
                elif value["group_by_type"] == "mean":
                    result = result.mean()
                elif value["group_by_type"] == "max":
                    result = result.max()
                elif value["group_by_type"] == "min":
                    result = result.min()

                result = (
                    result
                    .with_columns(
                        datestamp = pl.col("datetimestamp").dt.date(),
                        variable_id = pl.lit(value["new_var_id"])
                    )
                    .drop("datetimestamp")
                    # Filter negative values if they are not temperature measurements
                    .filter(
                        (pl.lit(key).str.contains("temp")) |
                        (pl.col("value") >= 0)
                    )
                    )

                if key == "daily_precip":
                    # daily_precip gets grouped by 06 to 18 hour of the next day, so they must be grouped accordingly.
                    result = (
                        result
                        .group_by(["station_id", "qa_id", "datestamp", "variable_id"])
                        .sum()
                        .filter(pl.col("datestamp") >= self.date_now.subtract(days=self.days).date())
                    )

                final_df.append(result.collect())
            except Exception as e:
                logger.error(f"Failed to calculate daily values out of hourly values for {key}! Error: {e}")
                raise RuntimeError(f"Failed to calculate daily values out of hourly values for {key}! Error: {e}")

        return pl.concat(final_df).select(["station_id", "qa_id", "datestamp", "variable_id", "value"])
