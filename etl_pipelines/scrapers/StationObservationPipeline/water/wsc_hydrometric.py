from scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from utils.constants import (
    logger,
    WSC_NAME,
    WSC_URL,
    WSC_DESTINATION_TABLES,
    WSC_STATION_SOURCE,
    WSC_DTYPE_SCHEMA
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
        self.station_source = WSC_STATION_SOURCE
        self.station_list = None
        self.expected_dtype = WSC_DTYPE_SCHEMA
        
        # Note that Once we use airflow this may have to change to a different way of getting the date especially if we want to use
        # it's backfill or catchup feature.
        date_now = datetime.now().strftime("%Y%m%d")
        self.source_url = {"wsc_daily_hydrometric.csv": WSC_URL.format(date_now)}

        self.end_date = datetime.now(pytz.timezone("UTC"))
        self.start_date = self.end_date - timedelta(days=self.days)

        self.get_station_list()
        

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
            df = downloaded_data_list["wsc_daily_hydrometric.csv"]
        except KeyError as e:
            logger.error(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect.", exc_info=True)
            raise KeyError(f"Error when trying to get the downloaded data from __downloaded_data attribute. The key wsc_daily_hydrometric.csv was not found, or the entered key was incorrect. Error: {e}")
        
        # apply some transformations that will be done to both the dataframes:
        df = (
            df
            .rename(colname_dict)
            .select(colname_dict.values())
            .with_columns((pl.col("datestamp").str.to_datetime("%Y-%m-%dT%H:%M:%S%:z")).alias("datestamp"))
            .filter(pl.col("datestamp") > self.start_date)
            .with_columns(pl.col("datestamp").dt.convert_time_zone("America/Vancouver"))
            .with_columns(pl.col("datestamp").dt.date())
        )

        # Apply transformations specific to the level values
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
        ).collect()
        
        # Apply transformations specific to the discharge values
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
        ).collect()
        
        # Set the transformed data
        self._EtlPipeline__transformed_data = {
            "level": [level_df, ["station_id", "datestamp"]],
            "discharge": [discharge_df, ["station_id", "datestamp"]]
        }


    def validate_downloaded_data(self):
        """
        Check the data that was downloaded to make sure that the column names are there and that the data types are as expected.

        Args:
            None

        Output:
            None
        """
        logger.debug(f"Validating the dowloaded data's column names and dtypes.")
        downloaded_data = self.get_downloaded_data()
        keys = list(downloaded_data.keys())
        columns = downloaded_data[keys[0]].collect_schema().names()
        dtypes = downloaded_data[keys[0]].collect_schema().dtypes()

        if not columns  == [' ID', 'Date', "Water Level / Niveau d'eau (m)", 'Grade', 'Symbol / Symbole', 'QA/QC', 'Discharge / Débit (cms)', 'Grade_duplicated_0', 'Symbol / Symbole_duplicated_0', 'QA/QC_duplicated_0']:
            raise ValueError(f"One of the column names in the downloaded dataset is unexpected! Please check and rerun")
        
        if not dtypes == [pl.String, pl.String, pl.Float32, pl.String, pl.String, pl.String, pl.Float32, pl.String, pl.String, pl.Int64]:
            raise TypeError(f"The type of a column in the downloaded data does not match the expected results! Please check and rerun")


