from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import(
    ENV_HYDRO_NAME,
    ENV_HYDRO_NETWORK,
    ENV_HYDRO_STAGE_BASE_URL,
    ENV_HYDRO_DISCHARGE_BASE_URL,
    ENV_HYDRO_STATION_SOURCE,
    ENV_HYDRO_DESTINATION_TABLES,
    ENV_HYDRO_DTYPE_SCHEMA,
    ENV_HYDRO_RENAME_DICT,
    ENV_HYDRO_MIN_RATIO,
    SPRING_DAYLIGHT_SAVINGS
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class EnvHydroPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=ENV_HYDRO_NAME,
            source_url=[],
            destination_tables=ENV_HYDRO_DESTINATION_TABLES,
            days=3,
            station_source=ENV_HYDRO_STATION_SOURCE,
            expected_dtype=ENV_HYDRO_DTYPE_SCHEMA,
            column_rename_dict=ENV_HYDRO_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype=True,
            network_ids= ENV_HYDRO_NETWORK,
            min_ratio=ENV_HYDRO_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )

        ## Add Implementation Specific attributes below
        self.source_url = {"discharge": ENV_HYDRO_DISCHARGE_BASE_URL, "stage": ENV_HYDRO_STAGE_BASE_URL}


    def transform_data(self):
        """
        Implementation of the transform_data method for the class EnvHydroPipeline. Since the downloaded data are two different files that will be inserted into two separate tables of the database, they will be transformed separately in this method.

        Args:
            None

        Output:
            None
        """

        logger.info("Starting Transformation Step")

        # Get downloaded data
        downloaded_data = self.get_downloaded_data()

        # Check that the downloaded data is not empty. If it is, something went wrong since it passed validation.
        if not downloaded_data:
            logger.error("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")
            raise RuntimeError("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")

        logger.info(f"Before transforming data, checking if there are new stations in the downloaded data")
        try:
            self.get_and_insert_new_stations()
        except Exception as e:
            # TODO: Send Failure email
            logger.error(f"There was an error when looking for/inserting new station metadata. Continuing without inserting new stations. Error: {e}")

        keys = list(downloaded_data.keys())
        for key in keys:
            df = downloaded_data[key]

            # Transform data
            try:
                df = (
                    df
                    .rename(self.column_rename_dict)
                    .remove(pl.col("datestamp").is_in(SPRING_DAYLIGHT_SAVINGS))
                    .with_columns((pl.col("datestamp").str.slice(offset=0, length=16)).str.to_datetime("%Y-%m-%d %H:%M", time_zone="UTC", ambiguous="earliest"))
                    .filter(
                        (pl.col("datestamp").dt.date() >= self.start_date.dt.date()) &
                        (pl.col("datestamp").dt.date() < self.end_date.dt.date()) &
                        (pl.col("value").is_not_nan()))
                    .with_columns(
                        datestamp = pl.col("datestamp").dt.date(),
                        qa_id = pl.when(pl.col('Grade').str.to_lowercase() == "unusable")
                            .then(0)
                            .otherwise(1),
                        variable_id = pl.when(pl.col("Parameter") == "Discharge")
                            .then(1)
                            .otherwise(2),
                        value = pl
                            .when((pl.col("Parameter") == "Discharge") & (pl.col("Unit") == "l/s")).then(pl.col("value") / 1000) # Convert to m^3/s
                            .when((pl.col("Parameter") == "Stage") & (pl.col("Unit") == "cm")).then(pl.col("value")/100) # Convert to m
                            .otherwise(pl.col("value"))
                    )
                    .join(self.station_list, on="original_id", how="left")
                )

                # Remove the new station data, and other columns that are not needed. Group by to get daily values
                df = (
                    df
                    .remove(pl.col("station_id").is_null())
                    .select(
                        pl.col("station_id"),
                        pl.col("datestamp"),
                        pl.col("value"),
                        pl.col("qa_id").cast(pl.Int8),
                        pl.col("variable_id").cast(pl.Int8)
                    )
                    .group_by(["station_id", "datestamp", "variable_id"]).agg([pl.mean("value"), pl.min("qa_id")])
                ).collect()

                # Assign to private attribute
                self._EtlPipeline__transformed_data[key] = {"df": df, "pkey": ["station_id", "datestamp"], "truncate": False}

            except Exception as e:
                logger.error(f"Error when trying to transform the downloaded data. Error: {e}", exc_info=True)
                raise Exception(f"Error when trying to transform the downloaded data. Error: {e}")

        logger.info(f"Transformation complete for both Discharge and Stage")


    def get_and_insert_new_stations(self):
        """
        This private method will check if there are any new stations in the downloaded data. If there are, then it will check that they are located within BC. If they are,
        then another check will be completed to see if they already exist under a different network id, if they do, only the new network_id will be inserted in to the database.
        If the station is completely new, all the metadata will be inserted in to the database.

        Args:
            None

        Output:
            None
        """
        try:
            new_stations = self.check_for_new_stations()
        except Exception as e:
            logger.error(f"Error when trying to check for new stations.")
            raise RuntimeError(e)

        if new_stations.limit(1).collect().is_empty():
            logger.info("No new stations found, going back to transformation")
            return

        # Make some adjustments to the dataset to get the lat and lon of the stations in to the new_stations list.
        new_stations = (
            pl.concat([
                new_stations
                .join(self._EtlPipeline__downloaded_data["discharge"].rename(self.column_rename_dict), on="original_id", how="inner")
                .drop("value"),
                new_stations
                .join(self._EtlPipeline__downloaded_data["stage"].rename(self.column_rename_dict), on="original_id", how="inner")
                .drop("value")
            ])
            .unique()
        )

        try:
            in_bc = self.check_new_station_in_bc(new_stations.select("original_id", "Longitude", "Latitude").unique())
        except Exception as e:
            logger.error("Error when trying to check if new stations are in BC.")
            raise RuntimeError(e)

        new_satations = (
            new_stations
            .filter(pl.col("original_id").is_in(in_bc))
        )

        if new_satations.limit(1).collect().is_empty():
            logger.info("No new stations found in BC, going back to transformation")
            return

        stage_discharge_filter = (
            new_stations
            .select(
                "original_id",
                "Parameter"
            )
            .unique()
            .group_by("original_id")
            .len()
            .filter(pl.col("len") == 2)
            .collect()
            .get_column("original_id")
        )

        # Remove any stations that were inserted in to the database with only the network_id. Also make changes so that constructing the insert tables are possible.
        new_stations = (
            new_stations
            .with_columns(
                station_status_id = 4,
                scrape = True,
                stream_name = pl.lit(None).cast(pl.String),
                station_description = pl.lit(None).cast(pl.String),
                operation_id = 1,
                drainage_area = None,
                regulated = False,
                user_flag = False,
                year = [self.date_now.year],
                project_id = [3,5,6],
                network_id = (pl
                    .when((pl.col("Latitude") < pl.lit(55.751226)) & (pl.col("Longitude") < pl.lit(-122.861447372))).then(53)
                    .otherwise(28)
                ),
                type_id = 1,
                variable_id = pl.when(
                    pl.col("original_id").is_in(stage_discharge_filter)
                    )
                    .then([1,2])
                    .when(
                        (~pl.col("original_id").is_in(stage_discharge_filter)) & (pl.col("Parameter") == pl.lit("Discharge"))
                    )
                    .then([1])
                    .otherwise([2])
            )
            .select(
                pl.col("original_id"),
                pl.col("Location Name").alias("station_name"),
                pl.col("station_status_id"),
                pl.col("Longitude").alias("longitude"),
                pl.col("Latitude").alias("latitude"),
                pl.col("scrape"),
                pl.col("stream_name"),
                pl.col("station_description"),
                pl.col("operation_id"),
                pl.col("drainage_area"),
                pl.col("regulated"),
                pl.col("user_flag"),
                pl.col("year"),
                pl.col("project_id"),
                pl.col("network_id"),
                pl.col("type_id"),
                pl.col("variable_id")
            )
        )
        try:
            new_stations, other_metadata_dict = self.construct_insert_tables(new_stations)
        except Exception as e:
            logger.error("Error when trying to construct insert tables.")
            raise RuntimeError(e)

        try:
            self.insert_new_stations(new_stations, other_metadata_dict)
        except Exception as e:
            logger.error(f"Error when trying to insert new stations. Error: {e}")
            raise RuntimeError(e)
