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
            bc_purpose = self.get_whole_table(table_name="licence_bc_purpose", has_geom=False)

            new_applications = (
                self.get_downloaded_data()[self.databc_layer_name]
                # Strip white spaces from ALL string type columns. name.keep() keeps the column name the same
                .with_columns((cs.string().str.strip_chars()).name.keep())
                .with_columns(
                    # Transform to 4326 since they are originally in 3005, ssame with latitude and longitude
                    geom4326 = pl.col("geometry").st.to_srid(4326),
                    latitude = pl.col("geometry").st.to_srid(4326).st.y(),
                    longitude = pl.col("geometry").st.to_srid(4326).st.x(),
                    water_allocation_type = (pl
                        .when(pl.col("pod_subtype") == pl.lit("POD"))
                        .then(pl.lit("SW"))
                        .when(pl.col("pod_subtype").is_in(["PWD", "PG"]))
                        .then(pl.lit("GW"))
                    ),
                    lic_status = pl.lit("ACTIVE APPL."),
                    purpose_code = (pl
                        .when((pl.col("purpose_use").is_null()) | (pl.col("purpose_use") == pl.lit("")))
                        .then(pl.lit("N/A"))
                        .otherwise(pl
                            .col("purpose_use")
                            .str.split(" - ")
                            .list.first()
                        )
                    ),
                    wrap_id = pl.col("wls_wra_sysid").cast(pl.String) + pl.lit("_wra")
                )
                .filter(
                    (pl.col("latitude").is_not_null()) &
                    (pl.col("longitude").is_not_null()) &
                    (pl.col("application_status") == pl.lit("Active Application"))
                )
                .select(
                    pl.col("wrap_id"),
                    pl.col("application_job_number").alias("licence_no"),
                    pl.col("pod_number").alias("tpod_tag"),
                    pl.col("water_allocation_type"),
                    pl.col("pod_diversion_type"),
                    pl.col("file_number").alias("file_no"),
                    pl.col("lic_status"),
                    pl.col("well_tag_number").cast(pl.Float64),
                    pl.col("purpose_code"),
                    pl.col("qty_diversion_max_rate"),
                    pl.col("qty_units_diversion_max_rate"),
                    pl.col("primary_applicant_name").alias("licensee"),
                    pl.col("latitude"),
                    pl.col("longitude"),
                    pl.col("district_precinct_name"),
                    pl.col("geom4326")
                )
            )

            new_applications_joined = (
                new_applications
                .join(
                    bc_purpose,
                    on="purpose_code",
                    how="left",
                    suffix="_purpose"
                )
                .join(
                    (
                        new_applications
                        .select(
                            "licence_no",
                            "tpod_tag",
                            "purpose_code",
                        )
                        .group_by(["licence_no", "tpod_tag", "purpose_code"]).len("count")
                        .with_columns(licensee = pl.lit("Multiple Licence Holders"))
                        .filter(pl.col("count") > 1)
                    ),
                    on=["licence_no", "tpod_tag", "purpose_code"],
                    how="left",
                    suffix="_mhl",
                    nulls_equal=True
                )
                .with_columns(
                    purpose = (pl
                        .when(pl.col("purpose_name").is_null() | (pl.col("purpose_name") == pl.lit("")))
                        .then(pl.lit("N/A"))
                        .otherwise(pl.col("purpose_name"))
                    ),
                    licensee = (pl
                        .when(pl.col("licensee_mhl").is_not_null())
                        .then(pl.col("licensee_mhl"))
                        .when(pl.col("licensee").is_null())
                        .then(pl.lit("Unnamed Licensee"))
                        .otherwise(pl.col("licensee"))
                    ),
                    industry_activity = (pl
                        .when(pl.col("general_activity_code").is_null())
                        .then(pl.lit("Other"))
                        .otherwise(pl.col("general_activity_code"))
                    ),
                    purpose_groups = (pl
                        .when(pl.col("general_activity_code").is_null())
                        .then(pl.lit("Other"))
                        .otherwise(pl.col("general_activity_code"))
                    ),
                    is_consumptive = (pl
                        .when(pl.col("is_consumptive").is_null())
                        .then(True)
                        .otherwise(pl.col("is_consumptive"))
                    ),
                    puc_groupings_storage = (pl
                        .when(pl.col("puc_groupings_storage").is_null())
                        .then(pl.lit("Other"))
                        .otherwise(pl.col("puc_groupings_storage"))
                    )
                )
                .unique(subset=["licence_no", "tpod_tag", "purpose"])
                .select(
                    "wrap_id",
                    "licence_no",
                    "tpod_tag",
                    "purpose",
                    "water_allocation_type",
                    "pod_diversion_type",
                    "file_no",
                    "lic_status",
                    "well_tag_number",
                    "qty_diversion_max_rate",
                    "qty_units_diversion_max_rate",
                    "licensee",
                    "latitude",
                    "longitude",
                    "district_precinct_name",
                    "geom4326",
                    "industry_activity",
                    "purpose_groups",
                    "is_consumptive",
                    "puc_groupings_storage"
                )
            )

            if not new_applications_joined.limit(1).collect().is_empty():
                self._EtlPipeline__transformed_data[self.databc_layer_name] = [new_applications_joined.collect() ["wrap_id"], True]
            else:
                logger.error(f"The DataFrame to be inserted in to the database for {self.name} was empty! This is not expected. The insertion will fail so raising error here")
                raise RuntimeError(f"The DataFrame to be inserted in to the database for {self.name} was empty! This is not expected. The insertion will fail")

        except Exception as e:
            logger.error(f"Failed to transform data for {self.name}. Error: {str(e)}")
            raise RuntimeError(f"Failed to transform data for {self.name}. Error: {str(e)}")

        self.update_import_date(data_source_name="water_rights_applications_public")

        logger.info(f"Transformation for {self.name} complete")
