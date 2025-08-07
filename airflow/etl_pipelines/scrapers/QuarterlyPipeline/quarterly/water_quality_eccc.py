from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_ECCC_DTYPE_SCHEMA,
    QUARTERLY_ECCC_BASE_URLS,
    QUARTERLY_ECCC_DESTINATION_TABLES,
    QUARTERLY_ECCC_NAME,
    QUARTERLY_ECCC_RENAME_DICT,
    QUARTERLY_ECCC_STATION_NETWORK_ID,
    QUARTERLY_ECCC_STATION_SOURCE,
    QUARTERLY_ECCC_MIN_RATIO,
    WATER_QUALITY_PARAMETER_DTYPE,
    ECCC_WATERQUALITY_NEW_PARAM_MESSAGE,
    MAX_NUM_RETRY
)
from etl_pipelines.utils.functions import setup_logging, reconnect_if_dead
from urllib.request import urlopen
from time import sleep
import polars as pl
import polars.selectors as cs
import pendulum
from psycopg2.extras import execute_values


logger = setup_logging()

class QuarterlyWaterQualityEcccPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=pendulum.now("UTC")):
        super().__init__(
            name=QUARTERLY_ECCC_NAME,
            source_url=QUARTERLY_ECCC_BASE_URLS,
            destination_tables=QUARTERLY_ECCC_DESTINATION_TABLES,
            days=2,
            station_source=QUARTERLY_ECCC_STATION_SOURCE,
            expected_dtype=QUARTERLY_ECCC_DTYPE_SCHEMA,
            column_rename_dict=QUARTERLY_ECCC_RENAME_DICT,
            go_through_all_stations=False,
            overrideable_dtype = True,
            network_ids=QUARTERLY_ECCC_STATION_NETWORK_ID,
            min_ratio=QUARTERLY_ECCC_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )

        self.get_all_stations_in_network()

    def download_data(self):
        """
        Downloads water quality data from the specified URLs in `source_url`.

        Args:
            None

        Output:
            None
        """

        logger.info(f"Downloading data for {self.name}")
        for key in self.source_url.keys():
            logger.debug(f"Downloading data from URL: {self.source_url[key]}")
            self._EtlPipeline__download_num_retries = 0
            failed = False

            while True:
                try:
                    response = urlopen(self.source_url[key])
                except Exception as e:
                    if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                        logger.warning(f"Error downloading data from URL: {self.source_url[key]}. Retrying...")
                        self._EtlPipeline__download_num_retries += 1
                        sleep(5)
                        continue
                    else:
                        logger.error(f"Error downloading data from URL: {self.source_url[key]}. Raising Error {e}", exc_info=True)
                        failed = True
                        break

                if response.status != 200:
                    if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                        logger.warning(f"Response status was not 200. Retrying...")
                        self._EtlPipeline__download_num_retries += 1
                        sleep(5)
                        continue
                    else:
                        logger.error(f"Response status was not 200. Raising Error {e}", exc_info=True)
                        failed = True
                        break

                break

            if failed:
                logger.error(f"Failed to download data from URL: {self.source_url[key]}. Please check for the errors and make fixes. Raising Error.")
                raise RuntimeError(f"Failed to download data from URL: {self.source_url[key]}. This was unexpected. Please Debug")

            try:
                logger.debug(f"Loading data into LazyFrame")
                lf = pl.scan_csv(response.read(), eol_char="\r\n", schema_overrides=self.expected_dtype[key], null_values=["NV", "Null", "NA", "N/A", "n/a", "IS", ""])
            except Exception as e:
                logger.error(f"Error when loading data in to LazyFrame, error: {e}")
                raise RuntimeError(f"Error when loading data in to LazyFrame, error: {e}")

            # Check if the data is empty
            if lf.limit(1).collect().is_empty():
                logger.error(f"Downloaded data is empty for URL: {self.source_url[key]}. This was not expected. Please check for the reason it is empty. Raising Error.")
                raise RuntimeError(f"Downloaded data is empty for URL: {self.source_url[key]}. This was not expected. Please check for the reason it is empty.")

            self._EtlPipeline__downloaded_data[key] = lf

        logger.info(f"Finished downloading data for {self.name}")

    def transform_data(self):
        """
        Transforms the downloaded water quality data into a format suitable for database insertion. The transformation process includes:
        - Renaming columns and stripping unwanted characters from string data
        - Joining with reference data for parameters, units, and stations
        - Filtering out invalid or null values
        - Converting and formatting datetimestamps
        - Assigning constant values for location purpose, sample state, and sample descriptor
        - Identifying and logging any missing parameters or units, and inserting new units into the database
        - Grouping and aggregating the data for insertion

        Args:
            None

        Output:
            None
        """

        logger.info(f"Starting transformation for {self.name}")
        downloaded_data = self.get_downloaded_data()

        logger.debug(f"Getting water quality parameters and water quality units")
        # Get these values to join to the data that has been downloaded
        self.db_conn = reconnect_if_dead(self.db_conn)

        try:
            params = pl.read_database(query="SELECT parameter_name, parameter_id FROM bcwat_obs.water_quality_parameter GROUP BY parameter_name, parameter_id;", connection=self.db_conn, schema_overrides=WATER_QUALITY_PARAMETER_DTYPE).lazy()
        except Exception as e:
            raise RuntimeError(f"Error when getting water quality parameter_id and parameter_name, error: {e}")

        # Get these values to join to the data that has been downloaded
        self.db_conn = reconnect_if_dead(self.db_conn)
        try:
            units = pl.read_database(query="SELECT unit_name, unit_id FROM bcwat_obs.water_quality_unit GROUP BY unit_name, unit_id;", connection=self.db_conn, schema_overrides=WATER_QUALITY_PARAMETER_DTYPE).lazy()
        except Exception as e:
            raise RuntimeError(f"Error when getting water quality unit_name and unit_name, error: {e}")

        all_missing_params = pl.LazyFrame()

        for key in downloaded_data.keys():
            logger.debug(f"Transforming data for key: {key}")

            data = (
                downloaded_data[key]
                .rename(self.column_rename_dict)
                .with_columns(
                    cs.by_dtype(pl.String).str.strip_chars('\n"')
                )
                .join(
                    other=params,
                    on="parameter_name",
                    how="left"
                )
                .join(
                    other=units,
                    on="unit_name",
                    how="left"
                )
                .join(
                    other=self.all_stations_in_network,
                    on="original_id",
                    how="inner"
                )
                .with_columns(
                    # This value is very weird sometimes and has the inequality operators attached to them, so remove them
                    value = pl.col("value").str.strip_chars("<>=").cast(pl.Float64)
                )
                .remove(
                    (pl.col("value").is_null()) |
                    (pl.col("value") == pl.lit(-999.9990)) |
                    # This is a special case with oxygenated water.
                    ((pl.col("SDL_LDE") == 1.0) & (pl.col("parameter_id") == 1763))
                )
                .with_columns(
                    datetimestamp = pl.col("datetimestamp").str.to_datetime("%Y-%m-%d %H:%M", time_zone="America/Vancouver"),
                    qa_id = (pl
                        .when(pl.col("STATUS_STATUT") == pl.lit("V")).then(1)
                        .otherwise(0)
                    ),
                    location_purpose = pl.lit("TREND"),
                    sample_state = pl.lit("Fresh Water"),
                    sample_descriptor = pl.lit("General"),

                )
                .select(
                    pl.col("station_id"),
                    pl.col("datetimestamp"),
                    pl.col("qa_id"),
                    pl.col("parameter_id"),
                    pl.col("parameter_name"),
                    pl.col("unit_id"),
                    pl.col("unit_name"),
                    pl.col("location_purpose"),
                    pl.col("sample_state"),
                    pl.col("sample_descriptor"),
                    pl.col("value"),
                    pl.col("FLAG_MARQUEUR").alias("value_letter")
                )
            )

            # Add all missing parameters to the collection of missing parameteres so that a notification can be made at the end of the transform function.
            missing_params = data.filter(pl.col("parameter_id").is_null()).select("parameter_name").unique()

            if not missing_params.limit(1).collect().is_empty() and all_missing_params.limit(1).collect().is_empty():
                all_missing_params = missing_params
            elif not missing_params.limit(1).collect().is_empty() and not all_missing_params.limit(1).collect().is_empty():
                all_missing_params = pl.concat([missing_params, all_missing_params])

            # Insert directly into database since it's not hard to insert units into the db.
            missing_units = data.filter(pl.col("unit_id").is_null()).select("unit_name").unique().collect()

            if not missing_units.is_empty():
                logger.info(f"The dataset consistd of new units, inserting them into the databases:\n{', '.join(missing_units.get_column("unit_name").to_list())}")

                query = """INSERT INTO bcwat_obs.water_quality_unit(unit_name) VALUES %s;"""

                try:
                    self.db_conn = reconnect_if_dead(self.db_conn)
                    cursor = self.db_conn.cursor()
                    execute_values(cur=cursor, sql=query, argslist=missing_units.rows())
                    self.db_conn.commit()
                except Exception as e:
                    logger.error(f"Failed to insert new units in to the databse! Error: {e}")
                    raise RuntimeError(f"Failed to insert new units in to the databse! Error: {e}")
                finally:
                    cursor.close()

                # Get the updated list of units
                self.db_conn = reconnect_if_dead(self.db_conn)
                try:
                    units = pl.read_database(query="SELECT unit_name, unit_id FROM bcwat_obs.water_quality_unit GROUP BY unit_name, unit_id;", connection=self.db_conn, schema_overrides=WATER_QUALITY_PARAMETER_DTYPE).lazy()
                except Exception as e:
                    raise RuntimeError(f"Error when getting water quality unit_name and unit_name, error: {e}")

                # rejoin the units lazyframe since it doesn't do post hast updates :(
                data = data.drop("unit_id").join(other=units, on="unit_name", how="inner")

            data = (
                data
                .filter(pl.col("parameter_id").is_not_null())
                .drop(
                    "parameter_name",
                    "unit_name"
                )
                .group_by(
                    ["station_id","datetimestamp","qa_id","parameter_id","unit_id","location_purpose","sample_state","sample_descriptor"]
                )
                .agg(
                    pl.col("value").max(),
                    pl.col("value_letter").drop_nulls().first()
                )
                .with_columns(
                    value_text =(pl
                        .when(pl.col("value_letter").is_not_null())
                        .then(pl.col("value_letter") + pl.lit(" ") + pl.col("value").cast(pl.String))
                        .otherwise(pl.col("value").cast(pl.String))
                    )
                )
            ).collect()

            self._EtlPipeline__transformed_data[key] = {"df": data, "pkey": ["station_id", "datetimestamp", "parameter_id", "unit_id"], "truncate": False}

        if not all_missing_params.limit(1).collect().is_empty():
            logger.warning(ECCC_WATERQUALITY_NEW_PARAM_MESSAGE)
            logger.warning(f"New Parameters: {', '.join(all_missing_params.get_column)}")


        logger.info(f"Finished transforming for {self.name}")
