from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from etl_pipelines.utils.constants import (
    WAP_NAME,
    WAP_LAYER_NAME,
    WAP_DTYPE_SCHEMA
)
from etl_pipelines.utils.functions import setup_logging
import polars_st as st
import polars as pl

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

        logger.info(f"Starting transformation for {self.name}")

        old_approvals = (
            self.get_whole_table(table_name="bc_wls_water_approval", has_geom=True)
            .with_columns(
                geom4326 = st.from_geojson("geojson").st.set_srid(4326),
                quantity_units =(pl
                    .when(
                        (pl.col("quantity_units") == pl.lit("m3/day")) &
                        (pl.col("approval_file_number") == pl.lit("6001989"))
                    )
                    .then(pl.lit("m3/year"))
                    .otherwise(pl.col("quantity_units"))
                )
            )
            .drop("geojson")
            .rename(lambda x: "old_" + x)
        )

        new_approvals = (
            self.get_downloaded_data()[self.databc_layer_name]
            .with_columns(
                geom4326 = pl.col("geometry").st.to_srid(4326),
                quantity_units =(pl
                    .when(
                        (pl.col("quantity_units").str.strip_chars() == pl.lit("m3/day")) &
                        (pl.col("approval_file_number") == pl.lit("6001989"))
                    )
                    .then(pl.lit("m3/year"))
                    .otherwise(pl.col("quantity_units").str.strip_chars())
                ),
                approval_type = pl.col("approval_type").str.strip_chars(),
                approval_file_number = pl.col("approval_file_number").str.strip_chars(),
                source = pl.col("source").str.strip_chars(),
                works_description = pl.col("works_description").str.strip_chars(),
                quantity = pl.col("quantity").str.strip_chars().cast(pl.Float64),
                qty_units_diversion_max_rate = (pl
                    .when(pl.col("qty_units_diversion_max_rate").str.strip_chars() == pl.lit("m3/s")).then(pl.lit("m3/sec"))
                    .when(pl.col("qty_units_diversion_max_rate").str.strip_chars() == pl.lit("m3/d")).then(pl.lit("m3/day"))
                    .otherwise(pl.col("qty_units_diversion_max_rate").str.strip_chars())
                ),
                water_district = pl.col("water_district").str.strip_chars(),
                precinct = pl.col("precinct").str.strip_chars(),
                approval_status = pl.col("approval_status").str.strip_chars(),
                application_date = pl.col("application_date").str.to_date("%Y-%m-%dZ"),
                fcbc_acceptance_date = pl.col("fcbc_acceptance_date").str.to_date("%Y-%m-%dZ"),
                approval_start_date = pl.col("approval_start_date").str.to_date("%Y-%m-%dZ"),
                approval_expiry_date = pl.col("approval_expiry_date").str.to_date("%Y-%m-%dZ")
            )
            .filter(
                (pl.col("approval_type") == pl.lit("STU")) &
                (pl.col("approval_status") == pl.lit("Current")) &
                (pl.col("quantity_units").is_in(["m3/year", "m3/day", "m3/sec"]))
            )
            .join_where(
                old_approvals,
                
            )
            .select(
                "wsd_region",
                "approval_type",
                "approval_file_number",
                "fcbc_tracking_number",
                "source",
                "works_description",
                "quantity",
                "quantity_units",
                "qty_diversion_max_rate",
                "qty_units_diversion_max_rate",
                "water_district",
                "precinct",
                "latitude",
                "longitude",
                "approval_status",
                "application_date",
                "fcbc_acceptance_date",
                "approval_issuance_date",
                "approval_start_date",
                "approval_expiry_date",
                "approval_refuse_abandon_date",
                "geom4326"
            )
        )




        logger.info(f"Transformation for {self.name} complete")

    def __some_private_function(self):
        pass
