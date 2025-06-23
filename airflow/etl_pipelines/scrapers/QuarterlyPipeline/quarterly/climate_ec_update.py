from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    HEADER,
    QUARTERLY_EC_BASE_URL,
    QUARTERLY_EC_NAME,
    QUARTERLY_EC_DESTINATION_TABLES,
    QUARTERLY_EC_DTYPE_SCHEMA,
    QUARTERLY_EC_STATION_SOURCE,
    QUARTERLY_EC_NETWORK_ID,
    QUARTERLY_EC_MIN_RATIO,
    QUARTERLY_EC_RENAME_DICT
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl
import polars.selectors as cs

logger = setup_logging()

class QuarterlyEcUpdatePipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=QUARTERLY_EC_NAME,
            source_url=[],
            destination_tables=QUARTERLY_EC_DESTINATION_TABLES,
            days=92,
            station_source=QUARTERLY_EC_STATION_SOURCE,
            expected_dtype=QUARTERLY_EC_DTYPE_SCHEMA,
            column_rename_dict=QUARTERLY_EC_RENAME_DICT,
            go_through_all_stations=True,
            overrideable_dtype=True,
            network_ids=QUARTERLY_EC_NETWORK_ID,
            min_ratio=QUARTERLY_EC_MIN_RATIO,
            file_encoding="utf8-lossy",
            db_conn=db_conn,
            date_now=date_now
        )

        # Get unique year-month combination to get the files we need to scrape
        year = list({self.date_now.subtract(days=x).year for x in range(self.days)})

        ## Add Implementation Specific attributes below
        self.source_url = {
            original_id + "_" + str(new_year): QUARTERLY_EC_BASE_URL.format(self.date_now.strftime("%Y%m%d"), original_id, new_year)
                for original_id in self.station_list.collect().get_column("original_id").to_list()
                    for new_year in year
        }

    def transform_data(self):
        """
        Transforms the downloaded data into a format suitable for database insertion. The transformation includes renaming columns, dropping
        unnecessary columns, unpivoting the data, casting data types, and filtering out invalid values. The transformed data is then split
        into different categories (temperature, precipitation, snow depth, and snow amount) based on `variable_id` and stored in
        the `__transformed_data` attribute.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Starting trasformation for {self.name}")

        data = self.get_downloaded_data()["station_data"]

        if data.limit(1).collect().is_empty():
            logger.error(f"No data was found in the attribute self._EtlPipeline__downloaded_data! Exiting with failure.")
            raise RuntimeError(f"No data was found in the attribute self._EtlPipeline__downloaded_data! Exiting with failure.")

        try:
            data = (
                data
                .rename(self.column_rename_dict)
                .drop(cs.contains("Flag", "Quality", "(", "Year", "Month", "Day", "Station"))
                .unpivot(index=["original_id", "datestamp"])
                .with_columns(
                    value = pl.col("value").replace("", None).cast(pl.Float64),
                    datestamp = pl.col("datestamp").str.to_date("%Y-%m-%d"),
                    variable_id = pl.col("variable").cast(pl.Int16),
                    qa_id = pl.lit(1)
                )
                .drop("variable")
                .remove(
                    (pl.col("value").is_null()) |
                    (pl.col("datestamp") < self.start_date.dt.date()) |
                    (pl.col("datestamp") > self.end_date.dt.date())
                )
                .join(self.station_list, on="original_id", how="inner")
                .select(
                    "station_id",
                    "datestamp",
                    "variable_id",
                    "value",
                    "qa_id"
                )
            ).collect()

        except Exception as e:
            logger.error(f"Failed to transform data for {self.name}. Exiting with failure.")
            raise RuntimeError(f"Failed to transform data for {self.name}. Exiting with failure.")

        try:
            self._EtlPipeline__transformed_data["temperature"] = {
                "df": data.filter(pl.col("variable_id").is_in([6, 7, 8])),
                "pkey": ["station_id", "datestamp", "variable_id"],
                "truncate": False
            }
        except Exception as e:
            logger.error(f"Failed to filter down to temperature data for {self.name}")
            raise RuntimeError(f"Failed to filter down to temperature data for {self.name}. Error {e}")

        try:
            self._EtlPipeline__transformed_data["precipitation"] = {
                "df": data.filter(pl.col("variable_id").is_in([27, 29])),
                "pkey": ["station_id", "datestamp", "variable_id"],
                "truncate": False
            }
        except Exception as e:
            logger.error(f"Failed to filter down to precipitation data for {self.name}")
            raise RuntimeError(f"Failed to filter down to precipitation data for {self.name}. Error {e}")

        try:
            self._EtlPipeline__transformed_data["snow_depth"] = {
                "df": data.filter(pl.col("variable_id").is_in([5])),
                "pkey": ["station_id", "datestamp"],
                "truncate": False
            }
        except Exception as e:
            logger.error(f"Failed to filter down to snow depth data for {self.name}")
            raise RuntimeError(f"Failed to filter down to snow depth data for {self.name}. Error {e}")

        try:
            self._EtlPipeline__transformed_data["snow_amount"] = {
                "df": data.filter(pl.col("variable_id").is_in([4])),
                "pkey": ["station_id", "datestamp"],
                "truncate": False
            }
        except Exception as e:
            logger.error(f"Failed to filter down to snow amount data for {self.name}")
            raise RuntimeError(f"Failed to filter down to snow amount data for {self.name}. Error {e}")

        logger.info(f"Finished transforming data for {self.name}")

    def get_and_insert_new_stations(self, station_data=None):
        # This method will not be implemented because the EC XML scraper should get all the new stations already.
        pass
