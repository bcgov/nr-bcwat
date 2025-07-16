from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    MSP_NAME,
    MSP_NETWORK,
    MSP_BASE_URL,
    MSP_DESTINATION_TABLES,
    MSP_STATION_SOURCE,
    MSP_DTYPE_SCHEMA,
    MSP_RENAME_DICT,
    MSP_MIN_RATIO,
    STR_MONTH_TO_INT_MONTH
)
from etl_pipelines.utils.functions import (
    setup_logging
)
import polars as pl

logger = setup_logging()

class MspPipeline(StationObservationPipeline):
    def __init__(self, db_conn = None, date_now = None):
        super().__init__(
            name=MSP_NAME,
            source_url=MSP_BASE_URL,
            destination_tables=MSP_DESTINATION_TABLES,
            days=2,
            station_source=MSP_STATION_SOURCE,
            expected_dtype=MSP_DTYPE_SCHEMA,
            column_rename_dict=MSP_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=False,
            network_ids= MSP_NETWORK,
            min_ratio=MSP_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )

    def transform_data(self):
        """
        This transform function is a bit different compared to the other scrapers' transform function. This is because the Manual Snow Pillow (MSP) is only taken once a month or so at each station. This means that new data rarely shows up, causing the dataframe that is supposed to be inserted to be empty. Furthermore, there are a few extra columns that needs to be inserted in to the table, so the MSP data is kept in it's own table, separate from the others. Other than the mentioned differences, the trasformation is mostly just formatting and filtering.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Starting Transformation for {self.name}")

        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")

        try:
            new_stations = self.check_for_new_stations().collect()

            if not new_stations.is_empty():
                # I know that the indentation here is odd. But since this is a string block, any tabs will show up in the message. The lack of indentation is for
                # formatting when the message is logged.
                logger.warning(f"""NOTICE: New stations for manual snow survey found. Please go to the following link with new stations IDs to get the metadata and insert them to the datatbase:
URL: https://aqrt.nrs.gov.bc.ca/Data/Location/Summary/Location/<original_id>/Interval/Latest
original_ids: {", ".join(new_stations["original_id"].to_list())}
The metadata that should be requested are:
    - Unique station ID
    - Station Name*
    - Station Type (surface water, ground water, climate, surface water quality, ground water quality, or msp)*
    - Station Operation (Continuous, Seasonal)
    - Longitude
    - Latitude
    - Drainage Area*
    - If Hydrometric, if the station is a regulated station or not*
    - Variables that are reported
The attributes with * are not required. Please ensure that the new stations are within BC before inserting!
Once the metadata has been collected, please insert the data to the correct tables. The tables that should get inserted into are the following:
    - station
    - station_project_id
    - station_variable
    - station_year
Where the network_id is the network that {self.name} is running on ({self.network[0]}) and the year can be the year that the new station that is found on. Please reference the tables:
    - station_variable
    - station_status
    - station_type
    - operation
To determine the correct values for the mentioned metadata values.""")
            else:
                logger.info(f"No new stations found. Moving on to transformation")
        except Exception as e:
            logger.error(f"Error when trying to check for new stations.")
            raise RuntimeError(e)

        df = downloaded_data["msp"]

        # Since there is only one data file to process, do it all at once.
        try:
            df = (
                df
                .rename(self.column_rename_dict)
                .unpivot(index = ["original_id", "station_name", "survey_date", "survey_period", "survey_code"])
                .with_columns(
                    survey_date = pl.col("survey_date").str.to_date(),
                    # Will do survey_period transformation in two parts, else it'll get hard to read
                    survey_period = pl.concat_str([
                        pl.col("survey_period").str.slice(offset=0, length=2),
                        (pl.col("survey_period").str.slice(offset=3).str.to_lowercase().replace_strict(STR_MONTH_TO_INT_MONTH, default=None))
                        ])
                        .str.to_datetime("%d%m")
                        .dt.date(),
                    variable_id = pl.when(pl.col("variable") == "sd")
                        .then(18)
                        .when(pl.col("variable") == "swe")
                        .then(19)
                        .when(pl.col("variable") == "percent_density")
                        .then(21)
                        .otherwise(None),
                    value = pl.col("value").cast(pl.Float64),
                    # According to the last old scraper, the original_id can have a "P" appended to the end of it, but be stored in the db without
                    # it. Did some simple regex style removal
                    # ie: '1B02P' is stored in the database as '1B02'
                    original_id = pl.col("original_id").str.replace(r"P$", ""),
                    qa_id = pl.lit(0)
                )
                .with_columns(
                    survey_period = pl.when(
                        (pl.col("survey_period").dt.date() == 1) &
                        (pl.col("survey_period").dt.month() == 1) &
                        (pl.col("survey_date").dt.month() == 12)
                    )
                    .then(pl.col("survey_period").dt.replace(year=pl.col("survey_date").dt.year() + 1))
                    .otherwise(pl.col("survey_period").dt.replace(year=pl.col("survey_date").dt.year()))
                )
                .filter(
                    pl.col("value").is_not_null() &
                    pl.col("variable_id").is_not_null() &
                    ((pl.col("survey_period") >= self.start_date.dt.date()) |
                    (pl.col("survey_date") >= self.start_date.dt.date()))
                )
                .join(self.station_list, on="original_id", how="inner")
                .select(
                    pl.col("station_id"),
                    pl.col("variable_id"),
                    pl.col("survey_period"),
                    pl.col("survey_date").alias("datestamp"),
                    pl.col("value"),
                    pl.col("survey_code").alias("code"),
                    pl.col("qa_id")
                )
            ).collect()

            self._EtlPipeline__transformed_data["msp"] = {"df": df, "pkey": ["station_id", "survey_period", "variable_id"], "truncate": False}

        except Exception as e:
            logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")

        logger.info(f"Transformation of {self.name} complete")
