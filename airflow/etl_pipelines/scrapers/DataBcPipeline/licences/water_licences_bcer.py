from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from etl_pipelines.utils.constants import (
    WL_BCER_NAME,
    WL_BCER_DTYPE_SCHEMA,
    WL_BCER_DESTINATION_TABLES,
    WL_BCER_URL,
    HEADER,
    MAX_NUM_RETRY
    )
from etl_pipelines.utils.functions import setup_logging
from time import sleep
from io import StringIO
import polars_st as st
import polars as pl
import polars.selectors as cs
import requests
import json

logger = setup_logging()

class WaterLicencesBCERPipeline(DataBcPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=WL_BCER_NAME,
            url=WL_BCER_URL,
            destination_tables=WL_BCER_DESTINATION_TABLES,
            databc_layer_name=None,
            expected_dtype=WL_BCER_DTYPE_SCHEMA,
            db_conn=db_conn,
            date_now=date_now
            )

        # Add other attributes as needed

    def download_data(self):
        """
        Download method specific for WaterLicenceBCERPipeline. This requires a different download method compared to the other DataBcPipeline scrapers because it does not get it's data from DataBC. It get's it's data from BC-ER's ArcGIS map as an GeoJSON file.
        The response is directly translated in to an Polars DataFrame. Since the data is in a JSON format, the data gets read in a struct format. That is why it needs to be unnested before validating the data types and columns.

        This download method will retry upto three times with a 30 second delay between each retry. If the last retry fails it will throw an error.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Starting download step for the scraper {self.name}")

        if self.source_url == None:
            logger.error(f"No source url provided for the scraper {self.name}")
            raise RuntimeError(f"No source url provided for the scraper {self.name}")

        failed = False
        while True:
            try:
                response = requests.get(self.source_url, stream=True, headers=HEADER, timeout=20)
            except Exception as e:
                if self.__EtlPipeline_download_num_retries < MAX_NUM_RETRY:
                    if self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                        logger.warning(f"Error downloading data from URL: {self.source_url}. Retrying...")
                        self._EtlPipeline__download_num_retries += 1
                        sleep(30)
                        continue
                    else:
                        logger.error(f"Error downloading data from URL: {self.source_url}. Error: {e}")
                        failed = True
                        break

            if response.status_code == 200:
                logger.debug(f"Request got 200 response code, moving on to loading data")
                break
            elif self._EtlPipeline__download_num_retries < MAX_NUM_RETRY:
                    logger.warning(f"Link status code is not 200 with URL {self.source_url}. Retrying...")
                    self._EtlPipeline__download_num_retries += 1
                    sleep(30)
                    continue
            else:
                logger.warning(f"Link status code is not 200 with URL {self.source_url}, continuing to next station")
                failed = True
                break

        if failed:
            logger.error(f"Failed to download data from URL: {self.source_url}")
            raise RuntimeError(f"Failed to download data from URL: {self.source_url}")

        try:
            logger.debug(f"Loading data from URL: {self.source_url} into GeoLazyFrame")
            # Read the GeoJSON data into a Polars DataFrame. The pl.read_json constructor only takes in object that has a .read() method.
            # that is why it is transformed in to StringIO object.
            data = (
                pl.read_json(StringIO(json.dumps(response.json()["features"])), infer_schema_length=None)
                .lazy()
                .with_columns(
                    # Unnest the attributes so that they each become a column
                    pl.col("properties").struct.unnest(),
                    # Convert the geometry struct to be a geometry column
                    geom4326 = (
                        st.from_geojson(pl.col("geometry").struct.json_encode())
                        .st.set_srid(4326)
                    )
                )
                .drop("type", "properties", "geometry")
                .rename(str.lower)
                .cast(self.expected_dtype["bcer"])
            )

        except Exception as e:
            logger.error(f"Error loading data from URL: {self.source_url} into a GeoLazyFrame. Error: {e}")
            raise RuntimeError(f"Error loading data from URL: {self.source_url} into a GeoLazyFrame. Error: {e}")

        if data.limit(1).collect().is_empty():
            logger.error(f"The data scraped from {self.source_url} is empty! Please check if it is actually empty.")
            raise ValueError(f"The data scraped from {self.source_url} is empty! Please check if it is actually empty.")
        else:
            self._EtlPipeline__downloaded_data["bcer"] = data

        logger.info(f"Finished download step for the scraper {self.name}")

    def transform_data(self):

        """
        Transforms the downloaded data for the BCER scraper into a format suitable for database insertion. The transformation process includes:
            - Adding a unique row index as 'short_term_approval_id'.
            - Converting date strings into date objects.
            - Calculating latitude and longitude from the geometry column.
            - Determining if the purpose is consumptive based on the 'purpose_desc'.
            - Filtering the data to include only active records with non-zero approved volumes.

        Args:
            None

        Output:
            None
        """

        logger.info(f"Starting transformation step for {self.name}")

        data = self.get_downloaded_data()["bcer"]

        try:
            data = (
                data
                # Add row index as the unique column ID
                .with_row_index("short_term_approval_id")
                .with_columns(
                    # Convert all dates into actual dates.
                    cs.contains("date").str.to_datetime("%Y-%m-%dT%H:%M:%SZ").dt.date(),
                    short_term_approval_id = pl.col("short_term_approval_id").cast(pl.String) + pl.lit("_bcogc"),
                    latitude = pl.col("geom4326").st.y(),
                    longitude = pl.col("geom4326").st.x(),
                    is_consumptive = (pl
                        .when(pl.col("purpose_desc").str.contains("stroage"))
                        .then(False)
                        .otherwise(True)
                    )
                )
                .filter(
                    (pl.col("status") == pl.lit("Active")) &
                    (pl.coalesce(pl.col("approved_volume_per_day"), pl.lit(1)) != 0) &
                    (pl.coalesce(pl.col("approved_total_volume"), pl.lit(1)) != 0)
                )
                .select(
                    "short_term_approval_id",
                    "geom4326",
                    "latitude",
                    "longitude",
                    "pod_number",
                    "short_term_water_use_num",
                    "water_source_type",
                    "water_source_type_desc",
                    "water_source_name",
                    "purpose",
                    "purpose_desc",
                    "approved_volume_per_day",
                    "approved_total_volume",
                    "approved_start_date",
                    "approved_end_date",
                    "status",
                    "application_determination_num",
                    "activity_approval_date",
                    "activity_cancel_date",
                    "legacy_ogc_file_number",
                    "proponent",
                    "authority_type",
                    "land_type",
                    "data_source",
                    "is_consumptive"
                )
            ).collect()

        except Exception as e:
            logger.error(f"Failed while transforming data for {self.name}. Error: {e}")
            raise RuntimeError(f"Failed while transforming data for {self.name}. Error: {e}")

        if data.is_empty():
            logger.error(f"The transformed data is empty. This should not be the case, please check what happened and rerun!")
            raise ValueError(f"The transformed dataframe is empty when it should not be. Please check why it is empty and rerun!")
        else:
            self._EtlPipeline__transformed_data["bcer"] = {"df": data, "pkey": ["short_term_approval_id"], "truncate": True}

        logger.info(f"Finished transformation step for {self.name}")
