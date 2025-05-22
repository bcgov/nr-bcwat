from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from etl_pipelines.utils.constants import (
    WAP_NAME,
    WAP_LAYER_NAME,
    WAP_DTYPE_SCHEMA
)
from etl_pipelines.utils.functions import setup_logging
import polars_st as st

logger = setup_logging()

class WaterApprovalPointsPipeline(DataBcPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=WAP_NAME,
            url="tempurl",
            destination_tables=["temp"],
            databc_layer_name=WAP_LAYER_NAME,
            expected_dtype=WAP_DTYPE_SCHEMA,
            db_conn=db_conn,
            date_now=date_now
        )

        # Add other attributes as needed

    def transform_data(self):
        pass

    def __some_private_function(self):
        pass
