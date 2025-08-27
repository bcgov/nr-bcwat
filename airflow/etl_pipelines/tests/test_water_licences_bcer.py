from etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer import WaterLicencesBCERPipeline
from etl_pipelines.tests.test_constants.shared_constants import(
    water_licence_coverage_poly
)
from etl_pipelines.utils.constants import(
    WL_BCER_DESTINATION_TABLES,
    WL_BCER_DTYPE_SCHEMA,
    WL_BCER_NAME,
    WL_BCER_URL
)
from etl_pipelines.tests.conftest import (
    MockDbConn,
    mock_get_whole_table
)
from freezegun import freeze_time
from mock import patch, MagicMock, PropertyMock
from callee import Contains
import polars as pl
import polars.testing as plt
import polars_st as st
import pendulum
import pytest
import json

@freeze_time("2025-08-26 00:00:00 UTC")
def test_initialization():
    # Initialize the pipeline
    pipeline = WaterLicencesBCERPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Assert all attributes in DataBcPipeline
    assert pipeline.date_now == pendulum.now("UTC")
    assert pipeline.databc_layer_name == None

    # Assert all attributes in EtlPipeline
    assert pipeline.name == WL_BCER_NAME
    assert pipeline.destination_tables == WL_BCER_DESTINATION_TABLES
    assert pipeline.expected_dtype == WL_BCER_DTYPE_SCHEMA
    assert pipeline.source_url == WL_BCER_URL
    assert isinstance(pipeline.db_conn, MockDbConn)
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}

@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer.sleep")
@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer.requests.get")
@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer.logger")
def test_download_data(
    fake_logger,
    fake_requests,
    no_sleep
):
    # Set mock for whole test
    no_sleep.return_value = None

    # Initialize the pipeline
    pipeline = WaterLicencesBCERPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Case there is no source URL
    pipeline.source_url = None

    with pytest.raises(RuntimeError, match=rf"No source url provided for the scraper {pipeline.name}"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Starting download step for the scraper {pipeline.name}")
    fake_logger.error.assert_called_once_with(f"No source url provided for the scraper {pipeline.name}")

    # Clean Up
    pipeline.source_url = WL_BCER_URL
    fake_logger.reset_mock()

    # Case where requests.get raises exception
    fake_requests.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=f"Failed to download data from URL: {pipeline.source_url}"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Starting download step for the scraper {pipeline.name}")
    fake_logger.warning.assert_any_call(f"Error downloading data from URL: {pipeline.source_url}. Retrying...")
    fake_logger.error.assert_any_call(Contains(f"Error downloading data from URL: {pipeline.source_url}."))
    fake_logger.error.assert_any_call(f"Failed to download data from URL: {pipeline.source_url}")

    assert fake_logger.warning.call_count == 3
    assert fake_logger.error.call_count == 2
    assert pipeline._EtlPipeline__download_num_retries == 3

    # Clean Up
    fake_logger.reset_mock()
    pipeline._EtlPipeline__download_num_retries = 0
    fake_requests.reset_mock(side_effect=True)

    # Case where status code not 200
    status_code = PropertyMock(return_value=404)
    type(fake_requests).status_code = status_code

    with pytest.raises(RuntimeError, match=f"Failed to download data from URL: {pipeline.source_url}"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Starting download step for the scraper {pipeline.name}")
    fake_logger.warning.assert_any_call(f"Link status code is not 200 with URL {pipeline.source_url}. Retrying...")
    fake_logger.error.assert_any_call(f"Link status code is not 200 with URL {pipeline.source_url}. Exiting with failure")
    fake_logger.error.assert_any_call(f"Failed to download data from URL: {pipeline.source_url}")

    assert fake_logger.warning.call_count == 3
    assert fake_logger.error.call_count == 2
    assert pipeline._EtlPipeline__download_num_retries == 3

    # Clean Up
    fake_logger.reset_mock()
    pipeline._EtlPipeline__download_num_retries = 0
    fake_requests.reset_mock(side_effect=True, return_value=True)

    # Case with status code 200, fails loading data
    fake_response = MagicMock()
    status_code = PropertyMock(return_value=200)

    fake_requests.return_value = fake_response
    type(fake_response).status_code = status_code
    fake_response.json.side_effect = Exception("Error")


    with pytest.raises(RuntimeError, match=rf"Error loading data from URL: {pipeline.source_url} into a GeoLazyFrame.*"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Starting download step for the scraper {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Request got 200 response code, moving on to loading data")
    fake_logger.debug.assert_any_call(f"Loading data from URL: {pipeline.source_url} into GeoLazyFrame")
    fake_logger.error.assert_called_once_with(Contains(f"Error loading data from URL: {pipeline.source_url} into a GeoLazyFrame."))

    # Clean Up
    fake_logger.reset_mock()
    fake_response.reset_mock(side_effect = True)
    fake_requests.reset_mock()

    # Successful run through
    fake_response = MagicMock()
    status_code = PropertyMock(return_value=200)

    fake_requests.return_value = fake_response
    type(fake_response).status_code = status_code
    fake_response.json.return_value = json.load(open("etl_pipelines/tests/test_constants/water_licence_csv/water_licences_bcer_download.geojson"))

    pipeline.download_data()

    assert len(pipeline._EtlPipeline__downloaded_data.keys()) == 1
    assert set(pipeline._EtlPipeline__downloaded_data.keys()) == {"bcer"}

    plt.assert_frame_equal(
        pipeline._EtlPipeline__downloaded_data["bcer"],
        (
            pl.scan_csv(
                "etl_pipelines/tests/test_constants/water_licence_csv/water_licences_bcer_download_output.csv",
                has_header=True,
                null_values=[""],
                schema_overrides={
                    'objectid': pl.Int64,
                    'pod_number': pl.String,
                    'short_term_water_use_num': pl.String,
                    'water_source_type': pl.String,
                    'water_source_type_desc': pl.String,
                    'water_source_name': pl.String,
                    'purpose': pl.String,
                    'purpose_desc': pl.String,
                    'approved_volume_per_day': pl.Float64,
                    'approved_total_volume': pl.Int64,
                    'approved_start_date': pl.String,
                    'approved_end_date': pl.String,
                    'status': pl.String,
                    'application_determination_num': pl.String,
                    'activity_approval_date': pl.String,
                    'activity_cancel_date': pl.String,
                    'legacy_ogc_file_number': pl.String,
                    'proponent': pl.String,
                    'authority_type': pl.String,
                    'land_type': pl.String,
                    'utm_zone': pl.String,
                    'utm_northing': pl.Float64,
                    'utm_easting': pl.Float64,
                    'data_source': pl.String,
                    'geom4326': pl.String
                }
            )
            .with_columns(
                geom4326=st.from_geojson("geom4326").st.set_srid(4326)
            )
        )
    )

@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer.gpd.read_postgis", )
@patch("etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer.logger")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.reconnect_if_dead", lambda conn: conn)
def test_transform_data(
    fake_logger,
    fake_read_postgis
):
    # Initialize scraper Object
    pipeline = WaterLicencesBCERPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Set downloaded data to be empty for now
    pipeline._EtlPipeline__downloaded_data["bcer"] = pl.LazyFrame()


    # Test correct error get's raised when no coverage_polygon is returned
    fake_read_postgis.return_value = None

    with pytest.raises(RuntimeError, match=r"Failed to get coverage_polygon:.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation step for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting coverage_polygon where watershed reports are supported")
    fake_logger.error.assert_called_once_with(Contains("Failed to get coverage_polygon:"), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_read_postgis.return_value = water_licence_coverage_poly

    # Test correct error get's thown when it fails in the transformation try block
    with pytest.raises(RuntimeError, match=r"Failed while transforming data for .*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation step for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting coverage_polygon where watershed reports are supported")
    fake_logger.error.assert_called_once_with(Contains(f"Failed while transforming data for {pipeline.name}."))

    # Clean Up
    fake_logger.reset_mock()

    # Check if empty case works
    pipeline._EtlPipeline__downloaded_data["bcer"] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/water_licence_csv/water_licences_bcer_download_output.csv",
            has_header=True
        )
        .with_columns(
            geom4326 = st.from_geojson(pl.col("geom4326")).st.set_srid(4326)
        )
        .cast(pipeline.expected_dtype["bcer"])
    ).head(0)

    with pytest.raises(ValueError, match=r"The transformed dataframe is empty when it should not be. Please check why it is empty and rerun!"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation step for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting coverage_polygon where watershed reports are supported")
    fake_logger.error.assert_any_call("The transformed data is empty. This should not be the case, please check what happened and rerun!")

    # Clean up
    fake_logger.reset_mock()

    # Successful case:
    pipeline._EtlPipeline__downloaded_data["bcer"] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/water_licence_csv/water_licences_bcer_download_output.csv",
            has_header=True,
            null_values=[""],
            schema_overrides={
                'objectid': pl.Int64,
                'pod_number': pl.String,
                'short_term_water_use_num': pl.String,
                'water_source_type': pl.String,
                'water_source_type_desc': pl.String,
                'water_source_name': pl.String,
                'purpose': pl.String,
                'purpose_desc': pl.String,
                'approved_volume_per_day': pl.Float64,
                'approved_total_volume': pl.Int64,
                'approved_start_date': pl.String,
                'approved_end_date': pl.String,
                'status': pl.String,
                'application_determination_num': pl.String,
                'activity_approval_date': pl.String,
                'activity_cancel_date': pl.String,
                'legacy_ogc_file_number': pl.String,
                'proponent': pl.String,
                'authority_type': pl.String,
                'land_type': pl.String,
                'utm_zone': pl.String,
                'utm_northing': pl.Float64,
                'utm_easting': pl.Float64,
                'data_source': pl.String,
                'geom4326': pl.String
            }
        )
        .with_columns(
            geom4326 = st.from_geojson(pl.col("geom4326")).st.set_srid(4326)
        )
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting transformation step for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting coverage_polygon where watershed reports are supported")
    fake_logger.info.assert_any_call(f"Finished transformation step for {pipeline.name}")
    fake_logger.error.assert_not_called()

    assert list(pipeline._EtlPipeline__transformed_data.keys()) == ["bcer"]
    assert set(pipeline._EtlPipeline__transformed_data["bcer"].keys()) == {"df", "pkey", "truncate"}
    assert pipeline._EtlPipeline__transformed_data["bcer"]["truncate"]
    assert pipeline._EtlPipeline__transformed_data["bcer"]["pkey"] == ["short_term_approval_id"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["bcer"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/water_licence_csv/water_licences_bcer_output.csv",
                null_values=[""],
                schema_overrides={
                    'short_term_approval_id': pl.String,
                    'geom4326': pl.String,
                    'latitude': pl.Float64,
                    'longitude': pl.Float64,
                    'pod_number': pl.String,
                    'short_term_water_use_num': pl.String,
                    'water_source_type': pl.String,
                    'water_source_type_desc': pl.String,
                    'water_source_name': pl.String,
                    'purpose': pl.String,
                    'purpose_desc': pl.String,
                    'approved_volume_per_day': pl.Float64,
                    'approved_total_volume': pl.Int64,
                    'approved_start_date': pl.Date,
                    'approved_end_date': pl.Date,
                    'status': pl.String,
                    'application_determination_num': pl.String,
                    'activity_approval_date': pl.Date,
                    'activity_cancel_date': pl.Date,
                    'legacy_ogc_file_number': pl.String,
                    'proponent': pl.String,
                    'authority_type': pl.String,
                    'land_type': pl.String,
                    'data_source': pl.String,
                    'is_consumptive': pl.Boolean
                }
            )
            .with_columns(
                geom4326 = st.from_geojson(pl.col("geom4326")).st.set_srid(4326)
            )
        ),
        check_column_order=False,
        check_row_order=False
    )
