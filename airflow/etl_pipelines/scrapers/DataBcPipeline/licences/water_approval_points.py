from etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline import DataBcPipeline
from etl_pipelines.utils.constants import (
    WAP_NAME,
    WAP_LAYER_NAME,
    WAP_DTYPE_SCHEMA,
    WAP_DESTINATION_TABLES,
    )
from etl_pipelines.utils.functions import setup_logging, reconnect_if_dead
import polars_st as st
import polars as pl
import polars.selectors as cs
import geopandas as gpd

logger = setup_logging()

class WaterApprovalPointsPipeline(DataBcPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=WAP_NAME,
            destination_tables=WAP_DESTINATION_TABLES,
            databc_layer_name=WAP_LAYER_NAME,
            expected_dtype=WAP_DTYPE_SCHEMA,
            db_conn=db_conn,
            date_now=date_now
        )

    def transform_data(self):
        """
        Tranformation method for the WaterApprovalPointsPipline class. This method will transform the data downloaded form DataBC in to the shape
        that is compatible with the bcwat_lic.bc_wls_water_approval table. The table is initially truncated since the old scraper was basically
        doing that in a round about way.
        The data from DataBC is filtered down to the approvals that we are interested in, and the approvals from
        bcwat_lic.wls_water_approval_deanna that are within the bcwat_lic.water_management_district_area are added on to the insertion list. Near
        the end of the method, th new water approval data are scanned for new units. If there are any, it will log an warning to notify to adjust
        the code accordingly.
        Finally, at the end the bcwat_lic.bc_data_import_date is updated to ensure that a record is kept on when it got last updated.

        Args:
            None

        Output:
            None
        """

        logger.info(f"Starting transformation for {self.name}")

        # Getting the shape of the current bc_wls_water_approval table so that the number of rows can be compared later.
        current_approvals_shape = self.get_whole_table(table_name="bc_wls_water_approval", has_geom=True).collect().shape

        self.db_conn = reconnect_if_dead(self.db_conn)
        try:
            logger.debug(f"Getting coverage_polygon where watershed reports are supported")
            coverage_polygon = st.from_geopandas(
                gpd.read_postgis(
                    sql="SELECT geom4326 AS geom4326 FROM bcwat_lic.water_licence_coverage",
                    con=self.db_conn,
                    geom_col="geom4326",
                    crs="EPSG:4326"
                )
            ).lazy()
        except Exception as e:
            logger.error(f"Failed to get coverage_polygon: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get coverage_polygon: {e}")

        try:
            # Getting the water approvals in the wls_water_approval_deanna table. The geojson column needs to be transformed into a geometry column
            deanna_approvals = (
                self.get_whole_table(table_name="wls_water_approval_deanna", has_geom=True)
                .with_columns(
                    geom4326 = st.from_geojson("geojson").st.set_srid(4326),
                )
                .drop("geojson")
            )

            # Similar to above but with the water_management_district_area
            water_management_area = (
                self.get_whole_table(table_name="water_management_district_area", has_geom=True)
                .with_columns(
                    geom4326 = st.from_geojson("geojson").st.set_srid(4326),
                )
                .drop("geojson")
            )

            # Join the two tables together if the point geometry in deanna_approvals is within the water_management_area
            deanna_in_management_area = (
                deanna_approvals
                .st.sjoin(water_management_area, on="geom4326", how="inner", predicate="within")
                .drop("geom4326_right")
                .with_row_index("bc_wls_water_approval_id")
                .with_columns(
                    wsd_region = pl.col("district_name"),
                    water_district = pl.col("district_name"),
                    approval_type = pl.lit("STU"),
                    bc_wls_water_approval_id = pl.col("bc_wls_water_approval_id").cast(pl.String) + pl.lit("_wa")
                )
                .st.sjoin(
                    other=coverage_polygon,
                    on="geom4326",
                    how="inner",
                    predicate="within"
                )
                .drop("geom4326_right")
                # Adding the polars row index as the bc_wls_water_approval_id
                .select(
                    pl.col("bc_wls_water_approval_id"),
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
                # Get downloaded data
                self.get_downloaded_data()[self.databc_layer_name]
                # Strip white spaces from ALL string type columns. name.keep() keeps the column name the same
                .with_columns((cs.string().str.strip_chars()).name.keep())
                # Change some date columns to date, and for the other date columns, remove the Z at the end of it
                .with_columns((
                    cs.by_name("application_date", "fcbc_acceptance_date", "approval_start_date", "approval_expiry_date")
                    .str.to_date("%Y-%m-%dZ")
                    ).name.keep(),
                    cs.by_name("approval_issuance_date", "approval_refuse_abandon_date").str.slice(offset=0, length=10).name.keep()
                )
                .with_row_index("bc_wls_water_approval_id", offset=deanna_in_management_area.shape[0]+1)
                .with_columns(
                    # Transform to 4326 since they are originally in 3005
                    geom4326 = pl.col("geometry").st.to_srid(4326),
                    latitude = pl.col("geometry").st.to_srid(4326).st.y(),
                    longitude = pl.col("geometry").st.to_srid(4326).st.x(),
                    # Special case for approval_file_number 6001989
                    quantity_units =(pl
                        .when(
                            (pl.col("quantity_units") == pl.lit("m3/day")) &
                            (pl.col("approval_file_number") == pl.lit("6001989"))
                        )
                        .then(pl.lit("m3/year"))
                        .otherwise(pl.col("quantity_units"))
                    ),
                    # fcbc_tracking_number is an integer. But for some reason the data source gives back a Float String, so needs to be
                    # cast to a float, to deal with the .0, then cast to int
                    fcbc_tracking_number = pl.coalesce(pl.col("fcbc_tracking_number"), pl.lit(0)).cast(pl.Float64).cast(pl.Int64),
                    quantity = pl.col("quantity").cast(pl.Float64),
                    qty_units_diversion_max_rate = (pl
                        .when(pl.col("qty_units_diversion_max_rate") == pl.lit("m3/s")).then(pl.lit("m3/sec"))
                        .when(pl.col("qty_units_diversion_max_rate") == pl.lit("m3/d")).then(pl.lit("m3/day"))
                        .otherwise(pl.col("qty_units_diversion_max_rate"))
                    ),
                    bc_wls_water_approval_id = pl.col("bc_wls_water_approval_id").cast(pl.String) + pl.lit("_wa")
                )
                # Add polars row index as bc_wls_water_approval_id, offset by the number of rows in deanna_in_management_area
                .filter(
                    (pl.col("approval_type") == pl.lit("STU")) &
                    (pl.col("approval_status") == pl.lit("Current")) &
                    (pl.col("quantity_units").is_in(["m3/year", "m3/day", "m3/sec"])) &
                    # Filter out the approvals that are already in the deanna_approval DF
                    (~pl.col("approval_file_number").is_in(deanna_approvals.collect().get_column("appfileno").unique().to_list()))
                )
                .select(
                    "bc_wls_water_approval_id",
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
            logger.debug("Trimming to the area that has watershed report covereage")

            new_approvals = (
                new_approvals
                .st.sjoin(
                    other=coverage_polygon.collect(),
                    on="geom4326",
                    how="inner",
                    predicate="within"
                )
                .drop("geom4326_right")
            )

        except Exception as e:
            logger.error(f"Failed to filter down by the coverage polygon for {self.name}! Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to filter down by the coverage polygon for {self.name}! Error: {e}")
        try:
            # Check if the new_approvals DF has any new units
            self._check_for_new_units((
                new_approvals
                    .select("quantity_units", "qty_units_diversion_max_rate")
                    .with_columns(
                        # Make a new column where the two unit columns are concatenated in to a list
                        units = pl.concat_list("quantity_units", "qty_units_diversion_max_rate")
                    )
                    .select("units")
                    # Make all list elements into separate rows.
                    .explode("units")
                ))

        except Exception as e:
            logger.error(f"There was an issue checking if there were new units in the rows to be inserted for {self.name}! Error: {e}")
            raise RuntimeError(f"There was an issue checking if there were new units in the rows to be inserted for {self.name}! Error: {e}")

        # Add the resulting DF's to the transformed data attribute
        if not new_approvals.is_empty():
            self._EtlPipeline__transformed_data["new_approval"] = {"df": new_approvals, "pkey": ["bc_wls_water_approval_id"], "truncate": True}

        if not deanna_in_management_area.is_empty():
            self._EtlPipeline__transformed_data["deanna_in_management_area"] = {"df": deanna_in_management_area, "pkey": ["bc_wls_water_approval_id"], "truncate": False}

        logger.info(f"The old approvals table had {current_approvals_shape[0]} rows in it. The new approval tables has {new_approvals.shape[0] + deanna_in_management_area.shape[0]} rows in it.")

        logger.info("Updating Import Date for the dataset wls_water_approvals")

        # Update the date that the import was last done.
        self.update_import_date("wls_water_approvals")

        logger.info(f"Transformation for {self.name} complete")
