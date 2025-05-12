from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    DRIVE_BC_DESTINATION_TABLES,
    DRIVE_BC_BASE_URL,
    DRIVE_BC_DTYPE_SCHEMA,
    DRIVE_BC_NAME,
    DRIVE_BC_NETWORK_ID,
    DRIVE_BC_RENAME_DICT,
    DRIVE_BC_STATION_SOURCE,
    STR_DIRECTION_TO_DEGREES
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

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
            db_conn=db_conn
            )

        

    def transform_data(self):
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
                .drop("received", "elevation", "event", "dataStatus")
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
                    precipLastHr = pl.when(pl.col("precipLastHr") == pl.lit("Yes"))
                        .then(1)
                        .otherwise(0),
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

        self._EtlPipeline__transformed_data["drive_bc"] = [df, ["station_id", "datetimestamp", "variable_id"]]

        logger.info("fin")
    def get_and_insert_new_stations(self, station_data=None):
        pass

