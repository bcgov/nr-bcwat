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

        # TODO: Check for new stations and insert them and associated metadata into the database here

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
                    ((pl.col("survey_period") >= self.start_date) |
                    (pl.col("survey_date") >= self.start_date))
                )
                .join(self.station_list, on="original_id", how="inner")
                .select(
                    pl.col("station_id"),
                    pl.col("variable_id"),
                    pl.col("survey_period"),
                    pl.col("survey_date").alias("datestamp"),
                    pl.col("value"),
                    pl.col("qa_id")
                )
            ).collect()

            self._EtlPipeline__transformed_data["msp"] = {"df": df, "pkey": ["station_id", "survey_period", "variable_id"], "truncate": False}

        except Exception as e:
            logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")

        logger.info(f"Transformation of {self.name} complete")

    def get_and_insert_new_stations(self, station_data=None):
        pass
