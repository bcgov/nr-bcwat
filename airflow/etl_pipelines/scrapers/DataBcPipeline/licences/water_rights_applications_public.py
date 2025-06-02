from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from etl_pipelines.utils.constants import (
    WRAP_DESTINATION_TABLES,
    WRAP_LAYER_NAME,
    WRAP_DTYPE_SCHEMA,
    WRAP_NAME
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl
import polars_st as st
import polars.selectors as cs

logger = setup_logging()

class WaterRightsApplicationsPublicPipeline(DataBcPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=WRAP_NAME,
            destination_tables=WRAP_DESTINATION_TABLES,
            databc_layer_name=WRAP_LAYER_NAME,
            expected_dtype=WRAP_DTYPE_SCHEMA,
            db_conn=db_conn,
            date_now=date_now
        )

        # Add other attributes as needed

    def transform_data(self):
        logger.info(f"Starting transformation for {self.name}")

        try:
            new_applications = (
                self.get_downloaded_data()[self.databc_layer_name]
            )


        except Exception as e:
            logger.error(f"Failed to transform data for {self.name}. Error: {str(e)}")
            raise RuntimeError(f"Failed to transform data for {self.name}. Error: {str(e)}")


        logger.info(f"Transformation for {self.name} complete")
