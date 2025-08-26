from etl_pipelines.scrapers.DataBcPipeline.licences.water_approval_points import WaterApprovalPointsPipeline
from etl_pipelines.tests.test_constants.shared_constants import(
    water_licence_coverage_poly
)
from etl_pipelines.utils.constants import(
    WAP_NAME,
    WAP_DESTINATION_TABLES,
    WAP_LAYER_NAME,
    WAP_DTYPE_SCHEMA
)
from etl_pipelines.tests.conftest import (
    MockDbConn,
    mock_get_whole_table
)
from freezegun import freeze_time
from mock import patch, MagicMock
import polars as pl
import polars.testing as plt
import polars.selectors as cs
import polars_st as st
import pendulum
import geopandas as gpd
import pytest


@freeze_time("2025-08-25 00:00:00 UTC")
def test_initialization():
    # Initialize the pipeline
    pipeline = WaterApprovalPointsPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Assert all attributes in DataBcPipeline
    assert pipeline.date_now == pendulum.now("UTC")
    assert pipeline.databc_layer_name == WAP_LAYER_NAME

    # Assert all attributes in EtlPipeline
    assert pipeline.name == WAP_NAME
    assert pipeline.destination_tables == WAP_DESTINATION_TABLES
    assert pipeline.expected_dtype == WAP_DTYPE_SCHEMA
    assert pipeline.source_url == None
    assert isinstance(pipeline.db_conn, MockDbConn)
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}

@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_approval_points.gpd.read_postgis", )
@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_approval_points.logger")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.DataBcPipeline._check_for_new_units")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.DataBcPipeline.get_whole_table")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.DataBcPipeline.update_import_date", MagicMock())
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.reconnect_if_dead", lambda conn: conn)
def test_transform_data(
    fake_get_whole_table,
    fake_check_units,
    mock_logger,
    fake_read_postgis,
    ):
    pipeline = WaterApprovalPointsPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))
    # set up initial patches
    fake_get_whole_table.side_effect = mock_get_whole_table
    fake_read_postgis.return_value = None

    with pytest.raises(RuntimeError, match=r"Failed to get coverage_polygon: .*"):
        pipeline.transform_data()

    mock_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    mock_logger.debug.assert_any_call("Getting coverage_polygon where watershed reports are supported")
    mock_logger.error.assert_called_once()

    # Clean up
    mock_logger.reset_mock()

    fake_read_postgis.return_value = water_licence_coverage_poly

    # Fail in the Transform step
    with pytest.raises(RuntimeError, match=r"Error finding new approvals by comparing the new approvals table to the current approvals table! .*"):
        pipeline.transform_data()

    mock_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    mock_logger.debug.assert_any_call("Getting coverage_polygon where watershed reports are supported")
    mock_logger.error.assert_called_once()

    # Clean Up
    mock_logger.reset_mock()

    # With valid downloaded data
    pipeline._EtlPipeline__downloaded_data["water-approval-points"] = (
        pl.scan_csv(
        "etl_pipelines/tests/test_constants/water_licence_csv/bc_wls_water_approval_download.csv",
        has_header=True
        )
        .with_columns(st.from_wkt(pl.col("geometry")).st.set_srid(3005))
        .cast(pipeline.expected_dtype["water-approval-points"])
    )

    # Fails checking for new units
    fake_check_units.side_effect = Exception("error")

    with pytest.raises(RuntimeError, match=r"There was an issue checking if there were new units in the rows to be inserted for.*"):
        pipeline.transform_data()

    mock_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    mock_logger.debug.assert_any_call("Getting coverage_polygon where watershed reports are supported")
    mock_logger.debug.assert_any_call("Trimming to the area that has watershed report covereage")
    mock_logger.error.assert_called_once()

    # Clean Up
    fake_check_units.side_effect = None
    mock_logger.reset_mock()

    # Success
    pipeline.transform_data()

    mock_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    mock_logger.debug.assert_any_call("Getting coverage_polygon where watershed reports are supported")
    mock_logger.debug.assert_any_call("Trimming to the area that has watershed report covereage")
    mock_logger.error.assert_not_called()
    mock_logger.info.assert_any_call("Updating Import Date for the dataset wls_water_approvals")
    mock_logger.info.assert_any_call(f"Transformation for {pipeline.name} complete")

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 2
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"deanna_in_management_area", "new_approval"}

    # Did the minimum number of transformations required to get the insert data and the verification data to match.
    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["new_approval"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/water_licence_csv/bc_wls_water_approval_new_approval.csv",
                schema_overrides={
                    'bc_wls_water_approval_id': pl.String,
                    'wsd_region': pl.String,
                    'approval_type': pl.String,
                    'approval_file_number': pl.String,
                    'fcbc_tracking_number': pl.Int64,
                    'source': pl.String,
                    'works_description': pl.String,
                    'quantity': pl.Float64,
                    'quantity_units': pl.String,
                    'qty_diversion_max_rate': pl.Float64,
                    'qty_units_diversion_max_rate': pl.String,
                    'water_district': pl.String,
                    'precinct': pl.String,
                    'latitude': pl.Float64,
                    'longitude': pl.Float64,
                    'approval_status': pl.String,
                    'application_date': pl.Date,
                    'fcbc_acceptance_date': pl.Date,
                    'approval_issuance_date': pl.String,
                    'approval_start_date': pl.Date,
                    'approval_expiry_date': pl.Date,
                    'approval_refuse_abandon_date': pl.String,
                    'geom4326': pl.String
                }
            )
            .with_columns(
                geom4326 = st.from_geojson(pl.col("geom4326")).st.set_srid(4326)
            )
        ),
        check_column_order=False,
        check_row_order=False
    )
    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["deanna_in_management_area"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/water_licence_csv/bc_wls_water_approval_deanna_in_management_area.csv",
                null_values=[""],
                schema_overrides={
                    "bc_wls_water_approval_id": pl.String,
                    "wsd_region": pl.String,
                    "water_district": pl.String,
                    "latitude": pl.Float64,
                    "longitude": pl.Float64,
                    "approval_type": pl.String,
                    "approval_file_number": pl.String,
                    "source": pl.String,
                    "works_description": pl.String,
                    "quantity": pl.Int64,
                    "quantity_units": pl.String,
                    "qty_diversion_max_rate": pl.Float64,
                    "qty_units_diversion_max_rate": pl.String,
                    "approval_status": pl.String,
                    "approval_start_date": pl.String,
                    "approval_expiry_date": pl.String,
                    "geom4326": pl.String,
                    "proponent": pl.String,
                    "podno": pl.String
                    }
            )
            .with_columns(
                geom4326 = st.from_geojson(pl.col("geom4326")).st.set_srid(4326),
            )
        ),
        check_column_order=False,
        check_row_order=False
    )

    assert  not pipeline._EtlPipeline__transformed_data["deanna_in_management_area"]["truncate"]
    assert pipeline._EtlPipeline__transformed_data["new_approval"]["truncate"]

    assert pipeline._EtlPipeline__transformed_data["deanna_in_management_area"]["pkey"] == ["bc_wls_water_approval_id"]
    assert pipeline._EtlPipeline__transformed_data["new_approval"]["pkey"] == ["bc_wls_water_approval_id"]
