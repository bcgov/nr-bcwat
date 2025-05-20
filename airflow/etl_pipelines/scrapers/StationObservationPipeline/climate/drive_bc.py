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
        self._EtlPipeline__transformed_data["drive_bc"] = [df, ["station_id", "datetimestamp", "variable_id"]]

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
