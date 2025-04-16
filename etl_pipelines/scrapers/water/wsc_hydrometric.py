from utils.etlpipeline_child_classes import StationObservationPipeline
from utils.constants import (
    logger,
    WSC_NAME,
    WSC_URL,
    WSC_DESTINATION_TABLES,
    WSC_STATION_SOURCE
)
from datetime import datetime, timedelta
import pytz
import polars as pl

class WscHydrometricPipeline(StationObservationPipeline):
    def __init__(self):
        # Initializing attributes in parent class
        super().__init__(name=WSC_NAME, source_url=[], destination_tables=WSC_DESTINATION_TABLES)

        # Initializing attributes present class
        self.days = 2
        self.station_list = super().get_station_list(station_source=WSC_STATION_SOURCE)
        
        # Note that Once we use airflow this may have to change to a different way of getting the date especially if we want to use
        # it's backfill or catchup feature.
        date_now = datetime.now().strftime("%Y%m%d")
        self.source_url = [["wsc_daily_hydrometric.csv", WSC_URL.format(date_now)]]

        self.end_date = datetime.now(pytz.timezone("UTC"))
        self.start_date = self.end_date - timedelta(days=self.days)
        

    def transform_data(self):
        """
        Implementation of the transform_data method for the class WscHydrometricPipeline. Since the downloaded data contains two different kinds of data that will be inserted into two separate tables of the database, common transformations have been made before splitting the data into two different dataframes. After which, the dataframes are transformed to match the schema of the database tables.

        Args: 
            None

        Output: 
            None
        """
        # Get the downloaded data
        downloaded_data_list = self.get_downloaded_data()

        # Check if there is any downloaded data if not raise an error
        if not downloaded_data_list:
            logger.error("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")
            raise RuntimeError("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")

        # Transform the data
        try:
            colname_dict = {" ID":"original_id", "Date":"datestamp", "Water Level / Niveau d'eau (m)":"level", "Discharge / Débit (cms)":"discharge"}
            df = downloaded_data_list[0]["wsc_daily_hydrometric.csv"]
        except KeyError as e:
            logger.error(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect.", exc_info=True)
            raise KeyError(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect. Error: {e}")
        
        # apply some transformations that will be done to both the dataframes:
        try:
            df = (
                df
                .rename(colname_dict)
                .select(colname_dict.values())
                .with_columns((pl.col("datestamp").str.to_datetime("%Y-%m-%dT%H:%M:%S%:z")).alias("datestamp"))
                .remove(pl.col("datestamp") <= self.start_date)
                .with_columns(pl.col("datestamp").dt.convert_time_zone("America/Vancouver"))
                .with_columns(pl.col("datestamp").dt.date())
            )
        except Exception as e:
            logger.error(f"Error when applying common transformations to the downloaded data for level and discharge.", exc_info=True)
            raise RuntimeError(f"Error when applying common transformations to the downloaded data for level and discharge. Error: {e}")

        # Apply transformations specific to the level values
        try:
            level_df = (
                df
                .select(pl.col("original_id"), pl.col("datestamp"), pl.col("level"))
                .rename({"level":"value"})
                .filter((pl.col("value").is_not_null()) & (pl.col("value") != 9999))
                .group_by(["original_id", "datestamp"]).mean()
                .with_columns(qa_id = 0, variable_id = 2)
                .join(self.station_list, on="original_id", how="inner")
                .drop(pl.col("original_id"))
                .select(pl.col("station_id"), pl.col("variable_id").cast(pl.Int8), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8))
            )
        except Exception as e:
            logger.error(f"Error when applying transformations to the level values.", exc_info=True)
            raise RuntimeError(f"Error when applying transformations to the level values. Error: {e}")
        
        # Apply transformations specific to the discharge values
        try:
            discharge_df = (
                df
                .select(pl.col("original_id"), pl.col("datestamp"), pl.col("discharge"))
                .rename({"discharge":"value"})
                .filter((pl.col("value").is_not_null()) & (pl.col("value") != 9999))
                .group_by(["original_id", "datestamp"]).mean()
                .with_columns(qa_id = 0, variable_id = 1)
                .join(self.station_list, on="original_id", how="inner")
                .drop(pl.col("original_id"))
                .select(pl.col("station_id"), pl.col("variable_id").cast(pl.Int8), pl.col("datestamp"), pl.col("value"), pl.col("qa_id").cast(pl.Int8))
            )
        except Exception as e:
            logger.error(f"Error when applying transformations to the discharge values.", exc_info=True)
            raise RuntimeError(f"Error when applying transformations to the discharge values. Error: {e}")

        # Set the transformed data
        self._EtlPipeline__transformed_data = {
            "level": [level_df, ["station_id", "datestamp"]],
            "discharge": [discharge_df, ["station_id", "datestamp"]]
        }


    def validate_downloaded_data(self):
        pass
