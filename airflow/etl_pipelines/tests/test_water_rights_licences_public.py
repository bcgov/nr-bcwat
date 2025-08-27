from etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_licences_public import WaterRightsLicencesPublicPipeline
from etl_pipelines.tests.test_constants.shared_constants import(
    water_licence_coverage_poly
)
from etl_pipelines.utils.constants import(
    WRLP_DESTINATION_TABLES,
    WRLP_DTYPE_SCHEMA,
    WRLP_LAYER_NAME,
    WRLP_NAME
)
from etl_pipelines.tests.conftest import (
    MockDbConn,
    mock_get_whole_table
)
from freezegun import freeze_time
from mock import patch, MagicMock
import polars as pl
import polars.testing as plt
import polars_st as st
import pendulum
import pytest

@freeze_time("2025-08-26 00:00:00 UTC")
def test_initialization():
    # Initialize the pipeline
    pipeline = WaterRightsLicencesPublicPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Assert all attributes in DataBcPipeline
    assert pipeline.date_now == pendulum.now("UTC")
    assert pipeline.databc_layer_name == WRLP_LAYER_NAME

    # Assert all attributes in EtlPipeline
    assert pipeline.name == WRLP_NAME
    assert pipeline.destination_tables == WRLP_DESTINATION_TABLES
    assert pipeline.expected_dtype == WRLP_DTYPE_SCHEMA
    assert pipeline.source_url == None
    assert isinstance(pipeline.db_conn, MockDbConn)
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}


@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_licences_public.gpd.read_postgis", )
@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_licences_public.logger")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.DataBcPipeline.get_whole_table")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.DataBcPipeline.update_import_date", MagicMock())
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.reconnect_if_dead", lambda conn: conn)
def test_transform_data(
    fake_get_whole_table,
    fake_logger,
    fake_read_postgis
):
    # Initialize scraper Object
    pipeline = WaterRightsLicencesPublicPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Case where it fails at start
    fake_get_whole_table.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=rf"Transformation for new water right licences for {pipeline.name} failed! This occured before the appurtenant land calculation.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.error.assert_called_once()

    # Clean up
    fake_logger.reset_mock()

    # Set up next case where it passes the first try except block
    fake_get_whole_table.side_effect = mock_get_whole_table
    fake_read_postgis.side_effect = Exception("Error")

    pipeline._EtlPipeline__downloaded_data[pipeline.databc_layer_name] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/water_licence_csv/water_licence_rights_public_downloaded.csv",
            has_header=True,
            null_values=[""]
        )
        .with_columns(
            geometry = st.from_geojson(pl.col("geometry")).st.set_srid(3005)
        )
        .cast(pipeline.expected_dtype[pipeline.databc_layer_name])
    ).head(0)

    # Check that the right error gets raised
    with pytest.raises(RuntimeError, match=r"Failed to get Cariboo coverage polygon to find the appurtenant land within the region.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.error.assert_called_once()

    # Clean Up
    fake_logger.reset_mock()
    fake_read_postgis.reset_mock(side_effect=True)

    fake_read_postgis.return_value = water_licence_coverage_poly

    # Fails collecting appurtenant land in new data
    with pytest.raises(RuntimeError, match=r"Failed when collecting appurtenant land data to be inserted in to bcwat_lic.licence_bc_app_land table!.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.error.assert_any_call("Collecting Appurtenant Land data failed! Raising Error. poly")

    # Clean up
    fake_logger.reset_mock()

    fake_read_postgis.return_value = water_licence_coverage_poly.rename_geometry("poly")

    # Empty insert dataframe
    with pytest.raises(RuntimeError, match=rf"The DataFrame to be inserted in to the database for {pipeline.name} was empty! This is not expected. The insertion will fail"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.error.assert_any_call(f"The DataFrame to be inserted in to the database for {pipeline.name} was empty! This is not expected. The insertion will fail so raising error here")
    fake_logger.warning.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()

    # Success Case with no new appurtenant land
    pipeline._EtlPipeline__downloaded_data[pipeline.databc_layer_name] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/water_licence_csv/water_licence_rights_public_downloaded.csv",
            has_header=True,
            null_values=[""]
        )
        .with_columns(
            geometry = st.from_geojson(pl.col("geometry")).st.set_srid(3005)
        )
        .cast(pipeline.expected_dtype[pipeline.databc_layer_name])
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.debug.assert_any_call("Updating ann_adjust value for licences")
    fake_logger.info.assert_any_call(f"Transformation for {pipeline.name} complete")
    fake_logger.error.assert_not_called()
    fake_logger.warning.assert_not_called()

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"water-rights-licences-public"}
    assert pipeline._EtlPipeline__transformed_data["water-rights-licences-public"]["truncate"]
    assert pipeline._EtlPipeline__transformed_data["water-rights-licences-public"]["pkey"] == ["wrlp_id"]

    expected_output =(
            pl.read_csv(
                "etl_pipelines/tests/test_constants/water_licence_csv/water_licence_rights_public_output.csv",
                has_header=True,
                null_values=[""],
                schema_overrides={
                    'wrlp_id': pl.String,
                    'licence_no': pl.String,
                    'tpod_tag': pl.String,
                    'purpose': pl.String,
                    'pcl_no': pl.String,
                    'qty_original': pl.Float64,
                    'qty_flag': pl.String,
                    'qty_units': pl.String,
                    'licensee': pl.String,
                    'lic_status_date': pl.Date,
                    'priority_date': pl.Date,
                    'expiry_date': pl.Date,
                    'longitude': pl.Float64,
                    'latitude': pl.Float64,
                    'stream_name': pl.String,
                    'quantity_day_m3': pl.Float64,
                    'quantity_sec_m3': pl.Float64,
                    'quantity_ann_m3': pl.Float64,
                    'lic_status': pl.String,
                    'rediversion_flag': pl.String,
                    'flag_desc': pl.String,
                    'file_no': pl.String,
                    'water_allocation_type': pl.String,
                    'pod_diversion_type': pl.String,
                    'geom4326': pl.String,
                    'water_source_type_desc': pl.String,
                    'hydraulic_connectivity': pl.String,
                    'well_tag_number': pl.Float64,
                    'related_licences': pl.String,
                    'industry_activity': pl.String,
                    'purpose_groups': pl.String,
                    'is_consumptive': pl.Boolean,
                    'ann_adjust': pl.Float64,
                    'qty_diversion_max_rate': pl.Float64,
                    'qty_units_diversion_max_rate': pl.String,
                    'puc_groupings_storage': pl.String
                }
            )
            .with_columns(
                geom4326 = st.from_geojson("geom4326").st.set_srid(4326)
            )
        )

    expected_output = (
        expected_output
        .drop("related_licences")
        .unique()
        .join(
            other = pl.concat([
                (expected_output
                .select("wrlp_id", "related_licences")
                .group_by("wrlp_id")
                .agg(pl.len(), pl.col("related_licences"))
                .filter((pl.col("len") > 1))
                .drop("len")),
                (expected_output
                .select("wrlp_id", "related_licences")
                .filter(pl.col("related_licences").is_not_null())
                .group_by("wrlp_id")
                .all())
            ]),
            on="wrlp_id",
            how="left"
        )
    )

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["water-rights-licences-public"]["df"],
        expected_output,
        check_column_order=False,
        check_row_order=False
    )

    # Clean up
    fake_logger.reset_mock()

    # Success with new appurtenant land
    pipeline._EtlPipeline__downloaded_data[pipeline.databc_layer_name] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/water_licence_csv/water_licence_rights_public_downloaded.csv",
            has_header=True,
            null_values=[""]
        )
        .with_columns(
            geometry = st.from_geojson(pl.col("geometry")).st.set_srid(3005),
            purpose_use = pl.when(pl.col("wls_wrl_sysid") == pl.lit(94887)).then(pl.lit("08A - test")).otherwise(pl.col("purpose_use")),
            purpose_use_code = pl.when(pl.col("wls_wrl_sysid") == pl.lit(94887)).then(pl.lit("08A")).otherwise(pl.col("purpose_use_code"))
        )
        .cast(pipeline.expected_dtype[pipeline.databc_layer_name])
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.debug.assert_any_call("Updating ann_adjust value for licences")
    fake_logger.info.assert_any_call(f"Transformation for {pipeline.name} complete")
    fake_logger.warning.assert_called_once()
    fake_logger.error.assert_not_called()

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 2
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"water-rights-licences-public", "appurtenant_land"}
    assert pipeline._EtlPipeline__transformed_data["water-rights-licences-public"]["truncate"]
    assert pipeline._EtlPipeline__transformed_data["water-rights-licences-public"]["pkey"] == ["wrlp_id"]
    assert not pipeline._EtlPipeline__transformed_data["appurtenant_land"]["truncate"]
    assert pipeline._EtlPipeline__transformed_data["appurtenant_land"]["pkey"] == ["licence_no"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["appurtenant_land"]["df"],
        pl.DataFrame({
            "licence_no": ["C132209"],
            "purpose": [["Stream Storage: Non-Power"]]
        })
    )
