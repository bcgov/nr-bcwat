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
        logger.info(f"Starting transformation for {self.name}")

        current_rights = self.get_whole_table(table_name="bc_wls_wrl_wra", has_geom=True)

        try:

            bc_purpose = self.get_whole_table(table_name="licence_bc_purpose", has_geom=False)
            bc_app_land = self.get_whole_table(table_name="licence_bc_app_land", has_geom=False)

            new_rights = (
                self.get_downloaded_data()[self.databc_layer_name]
                # Strip white spaces from ALL string type columns. name.keep() keeps the column name the same
                .with_columns((cs.string().str.strip_chars()).name.keep())
                .with_columns(
                    # Transform to 4326 since they are originally in 3005
                    geom4326 = pl.col("geometry").st.to_srid(4326),
                    latitude = pl.col("geometry").st.to_srid(4326).st.y(),
                    longitude = pl.col("geometry").st.to_srid(4326).st.x(),
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
                )
                .filter(
                    (pl.col("geom4326").is_not_null()) &
                    (pl.col("licence_status") == pl.lit("Current")) &
                    (pl.col("quantity_units").is_not_null())
                )
                .select(
                    pl.col("wls_wrl_sysid").cast(pl.String).alias("wls_wrl_wra_id"),
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
                    ann_adjust = pl.lit(None).cast(pl.Float64),
                    purpose = pl.coalesce(pl.col("purpose"), pl.lit("na")),
                    pcl_no = pl.coalesce(pl.col("pcl_no"), pl.lit("na")),
                    documentation = pl.lit(None).cast(pl.String),
                    documentation_last_checked = pl.lit(None).cast(pl.Datetime).dt.replace_time_zone(time_zone="UTC"),
                    quantity_ann_m3_storage_adjust = pl.lit(None).cast(pl.String)
                )
                .with_columns(
                    cs.contains("date").str.to_date("%Y-%m-%dZ").name.keep()
                )
                .unique(subset=["licence_no", "tpod_tag", "purpose_name", "pcl_no"])
                .select(
                    pl.col("wls_wrl_wra_id"),
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
                    pl.col("quantity_ann_m3_storage_adjust"),
                    pl.col("qty_diversion_max_rate"),
                    pl.col("qty_units_diversion_max_rate"),
                    pl.col("puc_groupings_storage"),
                    pl.col("documentation"),
                    pl.col("documentation_last_checked")
                )
            )

            keeping_from_old = (
                current_rights
                .with_columns(
                    purpose = pl.coalesce(pl.col("purpose"), pl.lit("na")),
                    pcl_no = pl.coalesce(pl.col("pcl_no"), pl.lit("na")),
                    geom4326 = st.from_geojson("geojson").st.set_srid(3005).st.to_srid(4326),
                    latitude = st.from_geojson("geojson").st.set_srid(3005).st.to_srid(4326).st.y(),
                    longitude = st.from_geojson("geojson").st.set_srid(3005).st.to_srid(4326).st.x(),
                    documentation = (pl
                        .when(pl.col("documentation").is_null())
                        .then(None)
                        .otherwise(pl.col("documentation").list.to_struct(n_field_strategy="first_non_null").struct.json_encode())
                    )
                )
                .drop("geojson")
                .filter((pl.col("lic_status") != "CURRENT"))
                .select(
                    pl.col("wls_wrl_wra_id").cast(pl.String),
                    pl.col("licence_no"),
                    pl.col("tpod_tag"),
                    pl.col("purpose"),
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
                    pl.col("industry_activity"),
                    pl.col("purpose_groups"),
                    pl.col("is_consumptive"),
                    pl.col("ann_adjust"),
                    pl.col("quantity_ann_m3_storage_adjust"),
                    pl.col("qty_diversion_max_rate"),
                    pl.col("qty_units_diversion_max_rate"),
                    pl.col("puc_groupings_storage"),
                    pl.col("documentation"),
                    pl.col("documentation_last_checked")
                )
            )

            old_and_new_rights = (
                pl.concat([
                    new_rights_joined,
                    keeping_from_old
                ])
                .with_columns(
                    wls_wrl_wra_id = (pl
                        .when(pl.col("lic_status") == "ACTIVE APPL.")
                        .then(pl.col("wls_wrl_wra_id") + pl.lit("_wra"))
                        .otherwise(pl.col("wls_wrl_wra_id") + pl.lit("_wrl"))
                    )
                )
            )

            appurtenant_land = (
                old_and_new_rights
                .filter(
                    (pl.col("purpose") == pl.lit("Stream Storage: Non-Power")) &
                    (pl.col("lic_status") == pl.lit("CURRENT"))
                )
                .select("licence_no")
                .unique()
                .join(
                    old_and_new_rights,
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

                self._EtlPipeline__transformed_data["appurtenant_land"] = [appurtenant_land, ["licence_no"]]
                # TODO: If sending emails, do it here and send an email instead of logging an Warning.




        except Exception as e:
            logger.error(f"Transformation for {self.name} failed! {e}")
            raise RuntimeError


        logger.info(f"Transformation for {self.name} complete")
