from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from etl_pipelines.utils.constants import (
    WRLP_DTYPE_SCHEMA,
    WRLP_DESTINATION_TABLES,
    WRLP_LAYER_NAME,
    WRLP_NAME,
    APPURTENTANT_LAND_REVIEW_MESSAGE
    )
from etl_pipelines.utils.functions import setup_logging
import polars_st as st
import polars as pl
import polars.selectors as cs

logger = setup_logging()

class WaterRightsLicencesPublicPipeline(DataBcPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=WRLP_NAME,
            destination_tables=WRLP_DESTINATION_TABLES,
            databc_layer_name=WRLP_LAYER_NAME,
            expected_dtype=WRLP_DTYPE_SCHEMA,
            db_conn=db_conn,
            date_now=date_now
        )

    def transform_data(self):
        """
        This is the transformation function for the WaterRightsLicencesPublicPipeline class. The transformation that is done is mostly just filtering the data that we do not want out. The tables bcwat_lic.licence_bc_purpose and bcwat_lic.licence_bc_app_land assists with the filteration.
        A separate table, appurtenant_land, is created to store data for future scraper runs to use. This is inserted and the user gets a warning log that presents them with some manual steps that needs to be completed. If there are no new appurtenant_land rows, the current bcwat_lic.licence_bc_app_land table is checked for any rows with the column appurtenant_land set to null. If so, the same warning is raised for the user.

        Args:
            None

        Output:
            None
        """
        logger.info(f"Starting transformation for {self.name}")

        try:

            # Get tables bcwat_lic.licence_bc_purpose and bcwat_lic.licence_bc_app_land that will help with filtering.
            bc_purpose = self.get_whole_table(table_name="licence_bc_purpose", has_geom=False)
            bc_app_land = self.get_whole_table(table_name="licence_bc_app_land", has_geom=False)

            new_rights = (
                self.get_downloaded_data()[self.databc_layer_name]
                # Strip white spaces from ALL string type columns. name.keep() keeps the column name the same
                .with_columns((cs.string().str.strip_chars()).name.keep())
                .with_columns(
                    # Transform to 4326 since they are originally in 3005, ssame with latitude and longitude
                    geom4326 = pl.col("geometry").st.to_srid(4326),
                    latitude = pl.col("geometry").st.to_srid(4326).st.y(),
                    longitude = pl.col("geometry").st.to_srid(4326).st.x(),
                    # The purpose code is taken from the purpose_use column because the code can be mapped to a description. So the description
                    # after the code is a bit redundent.
                    purpose_code = (pl
                        .when((pl.col("purpose_use").is_null()) | (pl.col("purpose_use") == pl.lit("")))
                        .then(pl.lit("N/A"))
                        .otherwise(pl
                            .col("purpose_use")
                            .str.split(" - ")
                            .list.first()
                        )
                    ),
                    stream_name = (pl
                        .when((pl.col("source_name").is_null()) | (pl.col("source_name").is_in(["", "unnamed", "Unnamed"])))
                        .then(pl.lit("Unknown"))
                        .otherwise(pl.col("source_name"))
                    ),
                    quantity_day_m3 = (pl
                        .when(pl.col("quantity_units") == pl.lit("m3/day"))
                        .then(pl.col("quantity"))
                        .otherwise(None)
                    ),
                    quantity_sec_m3 = (pl
                        .when(pl.col("quantity_units") == pl.lit("m3/sec"))
                        .then(pl.col("quantity"))
                        .otherwise(None)
                    ),
                    quantity_ann_m3 = (pl
                        .when(pl.col("quantity_units") == pl.lit("m3/day"))
                        .then(pl.col("quantity") * 365.25)
                        .when(pl.col("quantity_units") == pl.lit("m3/sec"))
                        .then(pl.col("quantity") * 60 * 60 * 24 * 365.25)
                        .otherwise(pl.col("quantity"))
                    ),
                    # Status of the licences. This is set because we will scrape active applications to the same table.
                    lic_status = pl.lit("CURRENT"),
                    water_allocation_type = (pl
                        .when(pl.col("pod_subtype") == pl.lit("POD"))
                        .then(pl.lit("SW"))
                        .when(pl.col("pod_subtype").is_in(["PWD", "PG"]))
                        .then(pl.lit("GW"))
                    ),
                    water_source_type_desc = (pl
                        .when(pl.col("pod_subtype") == pl.lit("POD"))
                        .then(pl.lit("Surface Water"))
                        .when(pl.col("pod_subtype") == pl.lit("PWD"))
                        .then(pl.lit("Well"))
                        .when(pl.col("pod_subtype") == pl.lit("PG"))
                        .then(pl.lit("Dugout, ditch, quarry, etc"))
                    ),
                    # This is unique for the layer, so if we scrape multiple layers into the same table, they will not be unique.
                    # Solved by appending the layer short hand to the end of the id.
                    wrlp_id = pl.col("wls_wrl_sysid").cast(pl.String) + pl.lit("_wrl")
                )
                .filter(
                    (pl.col("geom4326").is_not_null()) &
                    (pl.col("licence_status") == pl.lit("Current")) &
                    (pl.col("quantity_units").is_not_null())
                )
                # A lot of columns are correct but renamed in the table. So this is where the rename happens, as well as some type casting.
                .select(
                    pl.col("wrlp_id"),
                    pl.col("licence_number").alias("licence_no"),
                    pl.col("pod_number").alias("tpod_tag"),
                    pl.col("primary_licensee_name").alias("licensee"),
                    pl.col("licence_status_date").alias("lic_status_date"),
                    pl.col("priority_date"),
                    pl.col("expiry_date"),
                    pl.col("longitude"),
                    pl.col("latitude"),
                    pl.col("purpose_code"),
                    pl.col("stream_name"),
                    pl.col("quantity_day_m3"),
                    pl.col("quantity_sec_m3"),
                    pl.col("quantity_ann_m3"),
                    pl.col("lic_status"),
                    pl.col("rediversion_ind").alias("rediversion_flag"),
                    pl.col("quantity_flag").alias("qty_flag"),
                    pl.col("quantity_flag_description").alias("flag_desc"),
                    pl.col("file_number").alias("file_no"),
                    pl.col("water_allocation_type"),
                    pl.col("pod_diversion_type"),
                    pl.col("geom4326"),
                    pl.col("water_source_type_desc"),
                    pl.col("hydraulic_connectivity"),
                    pl.col("well_tag_number").cast(pl.Float64),
                    pl.col("quantity").alias("qty_original"),
                    pl.col("quantity_units").alias("qty_units"),
                    pl.col("permit_over_crown_land_number").alias("pcl_no"),
                    pl.col("qty_diversion_max_rate").cast(pl.Float64),
                    pl.col("qty_units_diversion_max_rate"),
                )
            )

            # Joining the tables that will assist with filtering on to the new_rights LazyFrame.
            new_rights_joined = (
                new_rights
                .join(
                    bc_purpose,
                    on="purpose_code",
                    how="left",
                    suffix="_purpose"
                )
                .join(
                    bc_app_land,
                    on="licence_no",
                    how="left",
                    suffix="_app_land"
                )
                .join(
                    (new_rights
                        .select(
                            "licence_no",
                            "tpod_tag",
                            "purpose_code",
                            "pcl_no"
                        )
                        .group_by(["licence_no", "tpod_tag", "purpose_code", "pcl_no"]).len("count")
                        .with_columns(licensee=pl.lit("Multiple Licence Holders"))
                        .filter(pl.col("count") > 1)
                    ),
                    on=["licence_no", "tpod_tag", "purpose_code", "pcl_no"],
                    how="left",
                    suffix="_mhl",
                    nulls_equal=True
                )
                .with_columns(
                    purpose_name = (pl
                        .when((pl.col("purpose_name").is_null()) | (pl.col("purpose_name") == pl.lit("")))
                        .then(pl.lit("N/A"))
                        .otherwise(pl.col("purpose_name"))
                    ),
                    licensee = (pl
                        .when(pl.col("licensee_mhl").is_not_null())
                        .then(pl.col("licensee_mhl"))
                        .otherwise(pl.col("licensee"))
                    ),
                    puc_groupings_storage = (pl
                        .when(pl.col("puc_groupings_storage").is_null())
                        .then(pl.lit("Other"))
                        .otherwise(pl.col("puc_groupings_storage"))
                    ),
                    # This will be populated later before it get's inserted
                    ann_adjust = pl.lit(None).cast(pl.Float64),
                    purpose = pl.coalesce(pl.col("purpose"), pl.lit("na")),
                    pcl_no = pl.coalesce(pl.col("pcl_no"), pl.lit("na")),
                    quantity_ann_m3_storage_adjust = pl.lit(None).cast(pl.String)
                )
                # Convert columns with "date" in the name to datetime
                .with_columns(
                    cs.contains("date").str.to_date("%Y-%m-%dZ").name.keep()
                )
                .unique(subset=["licence_no", "tpod_tag", "purpose_name", "pcl_no"])
                .select(
                    pl.col("wrlp_id"),
                    pl.col("licence_no"),
                    pl.col("tpod_tag"),
                    pl.col("purpose_name").alias("purpose"),
                    pl.col("pcl_no"),
                    pl.col("qty_original"),
                    pl.col("qty_flag"),
                    pl.col("qty_units"),
                    pl.col("licensee"),
                    pl.col("lic_status_date"),
                    pl.col("priority_date"),
                    pl.col("expiry_date"),
                    pl.col("longitude"),
                    pl.col("latitude"),
                    pl.col("stream_name"),
                    pl.col("quantity_day_m3"),
                    pl.col("quantity_sec_m3"),
                    pl.col("quantity_ann_m3"),
                    pl.col("lic_status"),
                    pl.col("rediversion_flag"),
                    pl.col("flag_desc"),
                    pl.col("file_no"),
                    pl.col("water_allocation_type"),
                    pl.col("pod_diversion_type"),
                    pl.col("geom4326"),
                    pl.col("water_source_type_desc"),
                    pl.col("hydraulic_connectivity"),
                    pl.col("well_tag_number"),
                    pl.col("related_licences"),
                    pl.col("general_activity_code").alias("industry_activity"),
                    pl.col("general_activity_code").alias("purpose_groups"),
                    pl.col("is_consumptive"),
                    pl.col("ann_adjust"),
                    pl.col("qty_diversion_max_rate"),
                    pl.col("qty_units_diversion_max_rate"),
                    pl.col("puc_groupings_storage"),
                )
            )

            # This functionality is originally just for Cariboo, but there is a good chance that it will be spread to the other areas as well. I need to talk to Ben about this but he is currently in California, so I'll talk to him when he gets back. But for now I'll just assume that the whole study region will adopt this functionality and do it for all regions.

            appurtenant_land = (
                new_rights_joined
                .filter(
                    (pl.col("purpose") == pl.lit("Stream Storage: Non-Power")) &
                    (pl.col("lic_status") == pl.lit("CURRENT"))
                )
                .select("licence_no")
                .unique()
                .join(
                    new_rights_joined,
                    on = "licence_no",
                    how = "full",
                    suffix = "_1"
                )
                .select(
                    "licence_no",
                    "purpose"
                )
                .unique()
                .group_by("licence_no")
                .agg([pl.col("purpose")])
                .join(
                    bc_app_land,
                    on = "licence_no",
                    how="anti",
                    suffix="_app"
                ).select(
                    "licence_no",
                    "purpose"
                )
                .filter(pl.col("licence_no").is_not_null())
            ).collect()

            if not appurtenant_land.is_empty():
                logger.warning(APPURTENTANT_LAND_REVIEW_MESSAGE)

                self._EtlPipeline__transformed_data["appurtenant_land"] = {"df": appurtenant_land, "pkey": ["licence_no"], "truncate": False}
                # TODO: If sending emails, do it here and send an email instead of logging an Warning.

            # Check if there are any lincence_nos in the bc_app_land that have null values in the appurtenant_land column.
            elif not bc_app_land.collect().filter(pl.col("appurtenant_land").is_null()).is_empty():
                logger.warning(APPURTENTANT_LAND_REVIEW_MESSAGE)

                # TODO: If sending emails, do it here and send an email instead of logging an Warning.

            if not new_rights_joined.limit(1).collect().is_empty():
                self._EtlPipeline__transformed_data[self.databc_layer_name] = {"df": new_rights_joined.collect(), "pkey": ["wrlp_id"], "truncate": True}

        except Exception as e:
            logger.error(f"Transformation for {self.name} failed! {e}")
            raise RuntimeError(f"Transformation for {self.name} failed! {e}")

        logger.info(f"Transformation for {self.name} complete")
