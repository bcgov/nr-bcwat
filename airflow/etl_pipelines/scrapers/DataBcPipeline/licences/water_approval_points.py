from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from etl_pipelines.utils.constants import (
    WAP_NAME,
    WAP_LAYER_NAME,
    WAP_DTYPE_SCHEMA,
    WAP_DESTINATION_TABLES,
    WAP_ATTRIBUTES_ALREADY_IN_DB
)
from etl_pipelines.utils.functions import setup_logging
import polars_st as st
import polars as pl
import polars.selectors as cs

logger = setup_logging()

class WaterApprovalPointsPipeline(DataBcPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=WAP_NAME,
            url="tempurl",
            destination_tables=WAP_DESTINATION_TABLES,
            databc_layer_name=WAP_LAYER_NAME,
            expected_dtype=WAP_DTYPE_SCHEMA,
            db_conn=db_conn,
            date_now=date_now
        )

        # Add other attributes as needed

    def transform_data(self):

        logger.info(f"Starting transformation for {self.name}")

        logger.info(f"Truncating table bcwat_lic.bc_wls_water_approval")

        current_approvals_shape = self.__get_bc_wls_water_approval_table().collect().shape

        truncate_query = """
            TRUNCATE bcwat_lic.bc_wls_water_approval;
        """

        try:
            cur = self.db_conn.cursor()
            cur.execute(truncate_query)
            self.db_conn.commit()
            cur.close()
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error trying to run truncate query {truncate_query}! Error: {e}", exc_info=True)
            raise RuntimeError(f"Error trying to run truncate query {truncate_query}! Error: {e}")

        try:
            deanna_approvals = (
                self.get_whole_table(table_name="wls_water_approval_deanna", has_geom=True)
                .with_columns(
                    geom4326 = st.from_geojson("geojson").st.set_srid(4326),
                )
                .drop("geojson")
            )

            water_management_area = (
                self.get_whole_table(table_name="water_management_district_area", has_geom=True)
                .with_columns(
                    geom4326 = st.from_geojson("geojson").st.set_srid(4326),
                )
                .drop("geojson")
            )

            deanna_in_management_area = (
                deanna_approvals
                .st.sjoin(water_management_area, on="geom4326", how="inner", predicate="within")
                .with_columns(
                    wsd_region = pl.col("wsd_region"),
                    water_district = pl.col("water_district"),
                    latitude = pl.col("geom4326").st.y(),
                    longitude = pl.col("geom4326").st.x(),
                    approval_type = pl.lit("STU")
                )
                .with_row_index("water_approval_id")
                .select(
                    pl.col("water_approval_id"),
                    pl.col("wsd_region"),
                    pl.col("water_district"),
                    pl.col("latitude"),
                    pl.col("longitude"),
                    pl.col("approval_type"),
                    pl.col("appfileno").alias("approval_file_number"),
                    pl.col("sourcename").alias("source"),
                    pl.col("purpose").alias("works_description"),
                    pl.col("quantity"),
                    pl.col("quantity_units"),
                    pl.col("qty_diversion_max_rate"),
                    pl.col("qty_units_diversion_max_rate"),
                    pl.col("approval_status"),
                    pl.col("startdate").alias("approval_start_date"),
                    pl.col("expirationdate").alias("approval_expiry_date"),
                    pl.col("geom4326"),
                    pl.col("proponent"),
                    pl.col("podno")
                )
            ).collect()

            new_approvals = (
                self.get_downloaded_data()[self.databc_layer_name]
                .with_columns((cs.string().str.strip_chars()).name.keep())
                .with_columns((
                    cs.by_name("application_date", "fcbc_acceptance_date", "approval_start_date", "approval_expiry_date")
                    .str.to_date("%Y-%m-%dZ")
                    ).name.keep(),
                    cs.by_name("approval_issuance_date", "approval_refuse_abandon_date").str.slice(offset=0, length=10).name.keep()
                )
                .with_columns(
                    geom4326 = pl.col("geometry").st.to_srid(4326),
                    quantity_units =(pl
                        .when(
                            (pl.col("quantity_units") == pl.lit("m3/day")) &
                            (pl.col("approval_file_number") == pl.lit("6001989"))
                        )
                        .then(pl.lit("m3/year"))
                        .otherwise(pl.col("quantity_units"))
                    ),
                    fcbc_tracking_number = pl.coalesce(pl.col("fcbc_tracking_number"), pl.lit(0)).cast(pl.Float64).cast(pl.Int64),
                    quantity = pl.col("quantity").cast(pl.Float64),
                    qty_units_diversion_max_rate = (pl
                        .when(pl.col("qty_units_diversion_max_rate") == pl.lit("m3/s")).then(pl.lit("m3/sec"))
                        .when(pl.col("qty_units_diversion_max_rate") == pl.lit("m3/d")).then(pl.lit("m3/day"))
                        .otherwise(pl.col("qty_units_diversion_max_rate"))
                    )
                )
                .with_row_index("water_approval_id", offset=deanna_in_management_area.shape[0]+1)
                .filter(
                    (pl.col("approval_type") == pl.lit("STU")) &
                    (pl.col("approval_status") == pl.lit("Current")) &
                    (pl.col("quantity_units").is_in(["m3/year", "m3/day", "m3/sec"])) &
                    (~pl.col("approval_file_number").is_in(deanna_approvals.collect().get_column("appfileno").unique().to_list()))
                )
                .select(
                    "water_approval_id",
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
            ).collect()

        except Exception as e:
            logger.error(f"Error finding new approvals by comparing the new approvals table to the current approvals table! Exiting, error: {e}")
            raise RuntimeError(f" Error finding new approvals by comparing the new approvals table to the current approvals table! This could be an error that happened in the current_approvals section, new_approvals section, or in the last insert_approvals section. Exiting, error: {e}")

        try:
            self.__check_for_new_units(new_approvals)

        except Exception as e:
            logger.error(f"There was an issue checking if there were new units in the inserted rows! Error: {e}")
            raise RuntimeError(f"There was an issue checking if there were new units in the inserted rows! Error: {e}")

        if not new_approvals.is_empty():
            self._EtlPipeline__transformed_data["new_approval"] = [new_approvals, ["water_approval_id"]]

        if not deanna_in_management_area.is_empty():
            self._EtlPipeline__transformed_data["deanna_in_management_area"] = [deanna_in_management_area, ["water_approval_id"]]

        logger.info(f"Transformation for {self.name} complete")

    def __get_bc_wls_water_approval_table(self):

        logger.info("Refreshing current water approvals LazyFrame")
        approvals = (
                self.get_whole_table(table_name="bc_wls_water_approval", has_geom=True)
                .with_columns(
                    geom4326 = st.from_geojson("geojson").st.set_srid(4326),
                    # Since the data is stored as a string in the db with a decimal point, a direct cast to Int doesn't work.
                    # So cast to Float first, then to Int.
                    fcbc_tracking_number = pl.coalesce(pl.col("fcbc_tracking_number"), pl.lit(0)).cast(pl.Float64).cast(pl.Int64),
                    source = pl.coalesce(pl.col("source"), pl.lit("N/A")),
                    approval_refuse_abandon_date = pl.coalesce(pl.col("approval_refuse_abandon_date"), pl.lit("N/A")),
                    approval_issuance_date = pl.coalesce(pl.col("approval_issuance_date"), pl.lit("N/A"))
                )
                .drop("geojson")
            )

        return approvals

    def __check_for_new_units(self, new_rows):
        new_units = (
            new_rows
            .select("quantity_units", "qty_units_diversion_max_rate")
            .with_columns(
                units = pl.concat_list("quantity_units", "qty_units_diversion_max_rate")
            )
            .select("units")
            .explode("units")
            .filter(
                (~pl.col("units").is_in(["m3/year", "m3/day", "m3/sec", "Total Flow"]))
            )
            .get_column("units")
            .unique()
            .to_list()
        )

        if new_units:
            logger.warning(f"New units were found in the inserted approvals! Please check them and adjust the code accordingly. If these units are not expected, please edit these values in the quantity_units, or qty_units_diversion_max_rate columns in the bcwat_lic.bc_wls_water_approval table manually with the correct conversions to the associated values (quantity, and qty_diversion_max_rate, respectively).\nUnits Found: {'\n'.join(new_units)}")

            # TODO: Implement email to notify that this happened if implementing email notifications.
