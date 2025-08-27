from etl_pipelines.scrapers.StationObservationPipeline.climate.env_aqn import EnvAqnPipeline
from etl_pipelines.tests.conftest import MockDbConn
from etl_pipelines.tests.test_constants.shared_constants import (
    get_station_list_default
)
from etl_pipelines.utils.constants import (
    ENV_AQN_DESTINATION_TABLES,
    ENV_AQN_BASE_URL,
    ENV_AQN_DTYPE_SCHEMA,
    ENV_AQN_MIN_RATIO,
    ENV_AQN_NAME,
    ENV_AQN_NETWORK_ID,
    ENV_AQN_RENAME_DICT,
    ENV_AQN_STATION_SOURCE,
    NEW_STATION_MESSAGE_FRAMEWORK
)
from etl_pipelines.tests.test_constants.test_aqn_constants import (
    downloaded_data,
    expected_output_df
)
from freezegun import freeze_time
from mock import patch, MagicMock
import polars as pl
import polars.testing as plt
import pytest
import pendulum

@freeze_time("2025-08-20 00:00:00 UTC")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.env_aqn.pl.read_database")
def test_initialization(mock_get_station_list):
    # Set up mocks
    mock_get_station_list.return_value = get_station_list_default

    # Default Initialization
    pipeline = EnvAqnPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == ENV_AQN_NAME
    assert pipeline.source_url == ENV_AQN_BASE_URL
    assert pipeline.destination_tables == ENV_AQN_DESTINATION_TABLES
    assert pipeline.days == 3
    assert pipeline.station_source == ENV_AQN_STATION_SOURCE
    assert pipeline.expected_dtype == ENV_AQN_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == ENV_AQN_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == ENV_AQN_NETWORK_ID
    assert pipeline.min_ratio == ENV_AQN_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}

    assert pipeline.date_now == pendulum.now("UTC")
    plt.assert_frame_equal(
        pl.select(pipeline.end_date),
        pl.select(pl.datetime(
            year=pendulum.now("UTC").year,
            month=pendulum.now("UTC").month,
            day=pendulum.now("UTC").day,
            hour=pendulum.now("UTC").hour,
            second=pendulum.now("UTC").second,
            time_zone=str(pendulum.now("UTC").tz)
        ))
    )
    plt.assert_frame_equal(
        pl.select(pipeline.start_date),
        pl.select(pl.datetime(
            year=pendulum.now("UTC").year,
            month=pendulum.now("UTC").month,
            day=pendulum.now("UTC").day-3,
            hour=pendulum.now("UTC").hour,
            second=pendulum.now("UTC").second,
            time_zone=str(pendulum.now("UTC").tz)
        ))
    )

    plt.assert_frame_equal(
        pipeline.station_list,
        get_station_list_default
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_new_station_in_bc")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_for_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.env_aqn.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.env_aqn.pl.read_database")
@freeze_time("2025-08-20 00:00:00 UTC")
def test_transform_data(
    mock_get_station_list,
    mock_logger,
    mock_check_for_new_stations,
    mock_check_new_station_in_bc
    ):
    # Set up mocks
    mock_get_station_list.return_value = get_station_list_default


    # Default Initialization
    pipeline = EnvAqnPipeline(db_conn=MockDbConn(), date_now=pendulum.now("UTC"))

    # Assert no downloaded data
    with pytest.raises(RuntimeError, match=r"No data was downloaded for.*"):
        pipeline.transform_data()

    # Test that the right error gets thrown when checking for new station fails
    mock_check_for_new_stations.return_value = Exception
    pipeline._EtlPipeline__downloaded_data = downloaded_data

    pipeline.transform_data()

    mock_logger.error.assert_any_call(f"Failed to check for new stations in the downloaded data for {pipeline.name}. Continuing on without checking.")

    mock_logger.reset_mock()

    # Test that the right info gets logged when there is no new stations
    mock_check_for_new_stations.return_value = pl.LazyFrame()

    pipeline.transform_data()

    mock_logger.info.assert_any_call(f"There is no new stations in the data downloaded for {pipeline.name}. Continuing On")

    mock_logger.reset_mock()

    # Test that the right info gets logged when there is no new stations in BC:
    mock_check_for_new_stations.return_value = pl.LazyFrame({"original_id": ["K"]})
    mock_check_new_station_in_bc.return_value = []

    pipeline.transform_data()

    mock_logger.info.assert_any_call("There were new stations but none of them were in BC. Continuing without notifying.")

    mock_logger.reset_mock()

    # Test that the right info gets logged when there is a new stations in BC:
    mock_check_for_new_stations.return_value = pl.LazyFrame({"original_id": ["K"]})
    mock_check_new_station_in_bc.return_value = ["K"]

    pipeline.transform_data()

    mock_logger.warning(NEW_STATION_MESSAGE_FRAMEWORK.format(pipeline.name, ", ".join(["K"]), "BC Government: Air Quality (https://www.env.gov.bc.ca/epd/bcairquality/aqo/csv/Hourly_Raw_Air_Data/)", "", pipeline.name, ", ".join(pipeline.network)))

    # Check that the right exception gets raised when it fails to transform the data in the first block
    mock_check_for_new_stations.return_value = pl.LazyFrame()
    pipeline._EtlPipeline__downloaded_data = {
        "temperature": pl.LazyFrame()
    }

    with pytest.raises(RuntimeError, match=r"Error when trying to transform the data for.*"):
        pipeline.transform_data()

    mock_logger.reset_mock()

    # Check success case
    pipeline._EtlPipeline__downloaded_data = downloaded_data

    pipeline.transform_data()

    mock_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    mock_logger.info.assert_any_call(f"There is no new stations in the data downloaded for {pipeline.name}. Continuing On")
    mock_logger.debug.assert_any_call(f"Starting Transformation")
    mock_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")

    assert list(pipeline._EtlPipeline__transformed_data.keys()) == ["station_data"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        expected_output_df,
        check_row_order=False,
        check_column_order=False
    )

