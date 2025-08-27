from etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_applications_public import WaterRightsApplicationsPublicPipeline
from etl_pipelines.utils.constants import(
    WRAP_DESTINATION_TABLES,
    WRAP_DTYPE_SCHEMA,
    WRAP_LAYER_NAME,
    WRAP_NAME
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

@freeze_time('2025-08-27 00:00:00 UTC')
def test_initialization():
    # Initialize the pipeline
    pipeline = WaterRightsApplicationsPublicPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Assert all attributes in DataBcPipeline
    assert pipeline.date_now == pendulum.now("UTC")
    assert pipeline.databc_layer_name == WRAP_LAYER_NAME

    # Assert all attributes in EtlPipeline
    assert pipeline.name == WRAP_NAME
    assert pipeline.destination_tables == WRAP_DESTINATION_TABLES
    assert pipeline.expected_dtype == WRAP_DTYPE_SCHEMA
    assert pipeline.source_url == None
    assert isinstance(pipeline.db_conn, MockDbConn)
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert True

@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_applications_public.logger")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.DataBcPipeline.get_whole_table")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.DataBcPipeline.update_import_date", MagicMock())
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.reconnect_if_dead", lambda conn: conn)
def test_transform_data(
    fake_get_whole_table,
    fake_logger
):
    # Initialize the pipeline
    pipeline = WaterRightsApplicationsPublicPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Give pipeline downloaded data, but empty for now
    pipeline._EtlPipeline__downloaded_data[pipeline.databc_layer_name] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/water_licence_csv/water_rights_applications_public_download.csv",
            has_header=True,
            null_values=[""]
        )
        .with_columns(
            geometry = st.from_geojson(pl.col("geometry")).st.set_srid(3005)
        )
        .cast(pipeline.expected_dtype[pipeline.databc_layer_name])
    ).head(0)

    # Case that it fails in the transfomation section
    fake_get_whole_table.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=rf"Failed to transform data for {pipeline.name}.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.error.assert_called_once()

    # Clean Up
    fake_logger.reset_mock()

    # Case where transformation completes but is empty
    fake_get_whole_table.side_effect = mock_get_whole_table

    with pytest.raises(RuntimeError, match=f"The DataFrame to be inserted in to the database for {pipeline.name} was empty! This is not expected. The insertion will fail"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation for {pipeline.name}")
    fake_logger.error.assert_any_call(f"The DataFrame to be inserted in to the database for {pipeline.name} was empty! This is not expected. The insertion will fail so raising error here")

    # Clean Up
    fake_logger.reset_mock()

    # Successful case
    pipeline._EtlPipeline__downloaded_data[pipeline.databc_layer_name] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/water_licence_csv/water_rights_applications_public_download.csv",
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
    fake_logger.info.assert_any_call(f"Transformation for {pipeline.name} complete")
    fake_logger.error.assert_not_called()
    fake_logger.warning.assert_not_called()

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"water-rights-applications-public"}
    assert pipeline._EtlPipeline__transformed_data["water-rights-applications-public"]["pkey"] == ["wrap_id"]
    assert pipeline._EtlPipeline__transformed_data["water-rights-applications-public"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["water-rights-applications-public"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/water_licence_csv/water_rights_applications_public_output.csv",
                has_header=True,
                null_values=[""],
                schema_overrides={
                    'wrap_id': pl.String,
                    'licence_no': pl.String,
                    'tpod_tag': pl.String,
                    'purpose': pl.String,
                    'water_allocation_type': pl.String,
                    'pod_diversion_type': pl.String,
                    'file_no': pl.String,
                    'lic_status': pl.String,
                    'well_tag_number': pl.Float64,
                    'qty_diversion_max_rate': pl.Float64,
                    'qty_units_diversion_max_rate': pl.String,
                    'licensee': pl.String,
                    'latitude': pl.Float64,
                    'longitude': pl.Float64,
                    'district_precinct_name': pl.String,
                    'geom4326': pl.String,
                    'industry_activity': pl.String,
                    'purpose_groups': pl.String,
                    'is_consumptive': pl.Boolean,
                    'puc_groupings_storage': pl.String
                }
            )
            .with_columns(
                geom4326 = st.from_geojson("geom4326").st.set_srid(4326)
            )
        ),
        check_column_order=False,
        check_row_order=False
    )
