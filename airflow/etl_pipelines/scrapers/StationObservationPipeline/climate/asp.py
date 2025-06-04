from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    ASP_DESTINATION_TABLES,
    ASP_BASE_URLS,
    ASP_DTYPE_SCHEMA,
    ASP_NAME,
    ASP_NETWORK,
    ASP_RENAME_DICT,
    ASP_STATION_SOURCE,
    ASP_MIN_RATIO
)
from etl_pipelines.utils.functions import (
    setup_logging
)
import polars as pl

logger = setup_logging()

class AspPipeline(StationObservationPipeline):
    def __init__(self, db_conn = None, date_now = None):
        super().__init__(
            name=ASP_NAME,
            source_url=ASP_BASE_URLS,
            destination_tables=ASP_DESTINATION_TABLES,
            days=3,
            station_source=ASP_STATION_SOURCE,
            expected_dtype=ASP_DTYPE_SCHEMA,
            column_rename_dict=ASP_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=False,
            network_ids= ASP_NETWORK,
            min_ratio=ASP_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )


    def validate_downloaded_data(self):
        """
        Same method as the method in StationObservationPipeline. The only difference is that the data get's reshaped a little bit.
        By default, the csv that is obtained has it's station IDs as it's columns and datetime as rows. This will be hard to work with later on so edit it before validation. Else we would have to make a dictionary of varying length, depending on the number of station IDs, which will not be ideal.

        Args:
            None

        Output:
            None
        """
        for key in self._EtlPipeline__downloaded_data.keys():
            self._EtlPipeline__downloaded_data[key] = (
                self._EtlPipeline__downloaded_data[key]
                .unpivot(index="DATE(UTC)")
            )

        super().validate_downloaded_data()

    def transform_data(self):
        """
        Implementation of transform data to transform the downloaded data in to the correct format. ASP has 4 variables:
            SW: Snow Water Equivalent
            SD: Snow Depth
            PC: Precipitation (Cumulative)
            TA: Temperature
        SW and SD will get it's average taken for the day, and PC max will be caluclated as well as it's average hourly value for that day. Temperature will get it's min, max and mean values for the day calculated.

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

        # TODO: Check for new stations and insert them and associated metadata into the database here

        for key in downloaded_data.keys():
            logger.debug(f"Transforming data for {key}")

            df = downloaded_data[key]

            try:
                # Apply transfromations that can be done to all data
                df = (
                    df
                    .rename(self.column_rename_dict)
                    .with_columns(
                        # Since the time is in UTC, we will start in UTC, but before we aggregate them into days, it will be converted to PST so
                        # that the whole PST day is in the row.
                        datestamp = pl.col("datestamp").str.to_datetime("%Y-%m-%d %H:%M", time_zone="UTC", ambiguous="earliest"),
                        qa_id = 0,
                        variable_id = pl.when(key == 'SW')
                            .then(16)
                            .when(key == 'SD')
                            .then(5)
                            .when(key == 'PC')
                            .then(28)
                            .when(key == 'TA')
                            .then(7)
                            .otherwise(None),
                        value = pl.col("value").cast(pl.Float64),
                        original_id = pl.col("original_id").str.slice(offset=0, length=5)
                    )
                    .filter(
                        # Special filter for "SW" exists since we don't want the negative values
                        (pl.col("datestamp") >= self.start_date.in_tz("UTC")) &
                        (pl.col("value").is_not_null()) &
                        (pl.col("value") != 99999) &
                        ((pl.col("value") >= 0) if key == 'SW' else True)
                    )
                    .join(self.station_list, on="original_id", how="inner")
                    .select(
                        pl.col("datestamp"),
                        pl.col("station_id"),
                        pl.col("value"),
                        pl.col("qa_id").cast(pl.Int8),
                        pl.col("variable_id").cast(pl.Int8)
                    )
                )

                if key in ["SW", "SD"]:
                    # Gathering the mean of SW or SD. Nothing too special here.
                    df = (
                        df
                        .with_columns(pl.col("datestamp").dt.date())
                        .group_by(["datestamp", "station_id", "variable_id", "qa_id"]).mean()
                    ).collect()

                elif key == "TA":
                    # Gathering the min, max, and mean of temperature.
                    df = pl.concat([
                        df
                            .with_columns(
                                pl.col("datestamp").dt.date(),
                                variable_id = pl.lit(6, pl.Int8)
                            )
                            .group_by(["datestamp", "station_id", "variable_id", "qa_id"]).min(),
                        df
                            .with_columns(pl.col("datestamp").dt.date())
                            .group_by(["datestamp", "station_id", "variable_id", "qa_id"]).mean(),
                        df
                            .with_columns(
                                pl.col("datestamp").dt.date(),
                                variable_id = pl.lit(8, pl.Int8)
                            )
                            .group_by(["datestamp", "station_id", "variable_id", "qa_id"]).max()
                    ]).collect()

                elif key == "PC":
                    # Sorting so that the data is in the correct order
                    df = df.sort(["station_id", "datestamp"]).collect()

                    df = pl.concat([
                        df
                            .with_columns(pl.col("datestamp").dt.date())
                            .group_by(["datestamp", "station_id", "variable_id", "qa_id"]).max(),
                        df
                            .filter(pl.col("value") > 0)
                            .with_columns(
                                # Takes the discrete difference shifted one "down". Since it was sorted, it will be nth - (n-1)th. Which will give
                                # the amount of precipitation that fell in the hour. We know that this method does not take into account missing
                                # days/hours, but this is how the old scrapers did it so we will continue to do it this way.
                                datestamp = pl.col("datestamp").dt.date(),
                                value = pl.col("value").diff(),
                                variable_id = pl.lit(27, pl.Int8),
                                shift_filter = (df.filter(pl.col("value") > 0).get_column("station_id") == df.filter(pl.col("value") > 0).shift(1).get_column("station_id"))
                            )
                            .filter(
                                # We are removing the first row, as well as the first time the station_id changes. This is the expected behavior
                                # because when we take the difference of nth - (n-1)th, the first time it will be null, which we need to remove.
                                # and the first time the station_id changes will be the first row with a new station_id.
                                # Also removing negative values, since there is not such thing as negative precipitation.
                                pl.col("shift_filter") & (pl.col("value") > 0)
                            )
                            .drop("shift_filter")
                            .group_by(["datestamp", "station_id", "variable_id", "qa_id"]).sum()
                    ])

                if key in ["SW", "SD"]:
                    self._EtlPipeline__transformed_data[key] = {"df": df, "pkey": ["station_id", "datestamp"], "truncate": False}
                else:
                    self._EtlPipeline__transformed_data[key] = {"df": df, "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False}

            except Exception as e:
                logger.error(f"Error when trying to transform the data for {self.name} with key {key}. Error: {e}", exc_info=True)
                raise RuntimeError(f"Error when trying to transform the data for {self.name} with {key}. Error: {e}")

        logger.info(f"Finished Transformation Step for {self.name}")


    def get_and_insert_new_stations(self, station_data=None):
        pass

    def __implementation_specific_private_func(self):
        pass
