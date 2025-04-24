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
    SPRING_DAYLIGHT_SAVINGS
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl

logger = setup_logging()

class EnvHydroPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(name=ENV_HYDRO_NAME, source_url=[], destination_tables=ENV_HYDRO_DESTINATION_TABLES)

        ## Add Implementation Specific attributes below
        self.days = 3
        self.network = ENV_HYDRO_NETWORK
        self.station_source = ENV_HYDRO_STATION_SOURCE
        self.expected_dtype = ENV_HYDRO_DTYPE_SCHEMA
        self.column_rename_dict = ENV_HYDRO_RENAME_DICT
        self.go_through_all_stations = False

        self.db_conn = db_conn
        
        self.date_now = date_now.in_tz("UTC")
        self.end_date = self.date_now.in_tz("America/Vancouver")
        self.start_date = self.end_date.subtract(days=self.days).start_of("day")

        self.source_url = {"discharge": ENV_HYDRO_DISCHARGE_BASE_URL, "stage": ENV_HYDRO_STAGE_BASE_URL}

        self.get_station_list()

        self.new_station = {}

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

        keys = list(downloaded_data.keys())
        units = {}
        params = {}
        for key in keys:
            df = downloaded_data[key]

            # Transform data
            try:
                df = (
                    df
                    .rename(self.column_rename_dict[key])
                    .remove(pl.col("datestamp").is_in(SPRING_DAYLIGHT_SAVINGS))
                    .with_columns((pl.col("datestamp").str.slice(offset=0, length=16)).str.to_datetime("%Y-%m-%d %H:%M", time_zone="UTC", ambiguous="earliest"))
                    .filter((pl.col("datestamp") >= self.start_date.in_tz("UTC")) & (pl.col("value").is_not_nan()))
                    .with_columns(
                        qa_id = pl.when(pl.col(' Grade').str.to_lowercase() == "unusable")
                            .then(0)
                            .otherwise(1),
                        variable_id = pl.when(pl.col(" Parameter") == "Discharge")
                            .then(1)
                            .otherwise(2),
                        value = pl
                            .when((pl.col(" Parameter") == "Discharge") & (pl.col(" Unit") == "l/s")).then(pl.col("value") / 1000) # Convert to m^3/s
                            .when((pl.col(" Parameter") == "Stage") & (pl.col(" Unit") == "cm")).then(pl.col("value")/100) # Convert to m
                            .otherwise(pl.col("value")),
                        datestamp = pl.col("datestamp").dt.date()
                    )
                    .join(self.station_list, on="original_id", how="left")
                )
                
                ## Get new stations from the data source
                self.new_station[key] = df.filter(pl.col("station_id").is_null())

                # Remove the new station data, and other columns that are not needed. Group by to get daily values
                df = (
                    df
                    .remove(pl.col("station_id").is_null())
                    .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
                    .group_by(["station_id", "datestamp"]).agg([pl.mean("value"), pl.min("qa_id"), pl.min("variable_id")])
                ).collect()
                
                # Assign to private attribute
                self._EtlPipeline__transformed_data[key] = [df, ["station_id", "datestamp"]]
            
            except Exception as e:
                logger.error(f"Error when trying to transform the downloaded data. Error: {e}", exc_info=True)
                raise Exception(f"Error when trying to transform the downloaded data. Error: {e}")

        # Check if there are new stations in either of the datasets.
        if not self.new_station["discharge"].limit(1).collect().is_empty() or not self.new_station["stage"].limit(1).collect().is_empty():
            logger.info("New stations found in the data, adding to station table if not already in table")
            self.__add_new_station()

        logger.info(f"Transformation complete for both Discharge and Stage")
            
    def __add_new_station(self):
        """
        Private function to insert the new station in to the database with as much of the metadata filled out.

        Args: 
            None

        Output: 
            None
        """
        # Get stations that are not supposed to be scraped
        self.get_no_scrape_list()

        # Trim the full data so that just the stations can be kept
        discharge_stations = (
            self.new_station["discharge"]
            .select(
                pl.col("original_id"), 
                pl.col(" Location Name").alias("station_name"), 
                pl.col(" Latitude").alias("latitude"),
                pl.col(" Longitude").alias("longitude"),
                pl.col(" Parameter").alias("parameter"),
                pl.col("variable_id")
            )
            .unique()
            .remove(pl.col("original_id").is_in(self.no_scrape_list))
        )
        
        # Similar to above
        stage_stations = (
            self.new_station["stage"]
            .select(
                pl.col("original_id"), 
                pl.col(" Location Name").alias("station_name"), 
                pl.col(" Latitude").alias("latitude"),
                pl.col(" Longitude").alias("longitude"),
                pl.col(" Parameter").alias("parameter"),
                pl.col("variable_id")
            )
            .unique()
            .remove(pl.col("original_id").is_in(self.no_scrape_list))
        )
        
        # Join the two station list from the datasets to get the total station list. This allows for checking which station has both
        # discharge and stage data
        station_all_info = (
            pl.concat([discharge_stations, stage_stations])
            .with_columns(
                network_id = 53,
                station_type_id = 1,
                station_description = pl.col("station_name"),
                station_status_id = 4,
                scrape = True,
                operation_id = None,
                drainage_area = None,
                year = self.date_now.year,
                project_id = 6
            )
        )

        # Check if there are actually new stations or they were just not supposed to be scraped
        if station_all_info.limit(1).collect().is_empty():
            logger.info("No new stations found that has not been added to the database alreadyt. Exiting")
            return
        
        # Building dataframe to insert in to the stations table.
        try:
            station_insert = (
                station_all_info
                .select(
                    pl.col("original_id"),
                    pl.col("station_name"),
                    pl.col("station_description"),
                    pl.col("network_id"),
                    pl.col("station_type_id"),
                    pl.col("station_status_id"),
                    pl.col("operation_id"),
                    pl.col("longitude"),
                    pl.col("latitude"),
                    pl.col("drainage_area"),
                    pl.col("scrape")
                )
                .unique("original_id")
            ).collect()
        except Exception as e:
            logger.error(f"Error trying to create station_insert dataframe. Error: {e}", exc_info=True)
            raise pl.exceptions.ComputeError(f"Error trying to create station_insert dataframe. Error: {e}")
        
        # Building dataframe to be inserted into the station_project_id table
        try:
            station_project_id_insert = (
                station_all_info
                .select(
                    pl.col("original_id"),
                    pl.col("project_id")
                )
                .unique("original_id")
            ).collect()
        except Exception as e:
            logger.error(f"Error trying to create station_project_id_insert dataframe. Error: {e}", exc_info=True)
            raise pl.exceptions.ComputeError(f"Error trying to create station_project_id_insert dataframe. Error: {e}")
        
        # Building dataframe to be inserted into the station_variable table
        try:
            station_variable_insert = (
                station_all_info
                .select(
                    pl.col("original_id"),
                    pl.col("variable_id")
                )
            ).collect()
        except Exception as e:
            logger.error(f"Error trying to create station_variable_insert dataframe. Error: {e}", exc_info=True)
            raise pl.exceptions.ComputeError(f"Error trying to create station_variable_insert dataframe. Error: {e}")

        # Building dataframe to be inserted into the station_year table
        try:
            station_year_insert = (
                station_all_info
                .select(
                    pl.col("original_id"),
                    pl.col("year")    
                )
                .unique("original_id")
            ).collect()
        except Exception as e:
            logger.error(f"Error trying to create station_year_insert dataframe. Error: {e}", exc_info=True)
            raise pl.exceptions.ComputeError(f"Error trying to create station_year_insert dataframe. Error: {e}")

        # Insert the new stations and corresponding metadata
        try:
            logger.info(f"Adding new station to the station table for the scraper {self.name}")
            self.insert_new_stations(station_insert, station_project_id_insert, station_variable_insert, station_year_insert)
        except Exception as e:
            logger.error(f"Error when trying to add new station to the station table. Error: {e}", exc_info=True)

        # After successful metedata insert, add the removed data back into the private variable that will be inserted in to the database.
        logger.info(f"Concatting the new station data to the transformed data for both Discharge and Stage")
        self.new_station["discharge"] = (
            self.new_station["discharge"]
            .drop("station_id")
            .join(self.station_list, on="original_id", how="inner")
            .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
            .group_by(["station_id", "datestamp"]).agg([pl.mean("value"), pl.min("qa_id"), pl.min("variable_id")])
        ).collect()
        
        self.new_station["stage"] = (
            self.new_station["stage"]
            .drop("station_id")
            .join(self.station_list, on="original_id", how="inner")
            .select(pl.col("station_id"), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8), pl.col("variable_id").cast(pl.Int8))
            .group_by(["station_id", "datestamp"]).agg([pl.mean("value"), pl.min("qa_id"), pl.min("variable_id")])
        ).collect()

        self._EtlPipeline__transformed_data["discharge"][0] = (
            pl.concat(
                [
                    self._EtlPipeline__transformed_data["discharge"][0], 
                    self.new_station["discharge"]
                    ]
            )
        )
        self._EtlPipeline__transformed_data["stage"][0] = (
            pl.concat(
                [
                    self._EtlPipeline__transformed_data["stage"][0], 
                    self.new_station["stage"]
                    ]
            )
        )
