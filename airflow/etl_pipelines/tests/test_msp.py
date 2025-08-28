from etl_pipelines.scrapers.StationObservationPipeline.climate.msp import MspPipeline
from etl_pipelines.utils.constants import(
    MSP_BASE_URL,
    MSP_DESTINATION_TABLES,
    MSP_DTYPE_SCHEMA,
    MSP_MIN_RATIO,
    MSP_NAME,
    MSP_NETWORK,
    MSP_RENAME_DICT,
    MSP_STATION_SOURCE
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch
from callee import Contains
import polars as pl
import polars.testing as plt
import pendulum
import pytest

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.msp.pl.read_database")
@freeze_time("2025-04-30 00:00:00 UTC")
def test_initialization(fake_get_station_list):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/msp_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = MspPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == MSP_NAME
    assert pipeline.source_url == MSP_BASE_URL
    assert pipeline.destination_tables == MSP_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == MSP_STATION_SOURCE
    assert pipeline.expected_dtype == MSP_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == MSP_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert not pipeline.overrideable_dtype
    assert pipeline.network == MSP_NETWORK
    assert pipeline.min_ratio == MSP_MIN_RATIO
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
            day=pendulum.now("UTC").day-2,
            hour=pendulum.now("UTC").hour,
            second=pendulum.now("UTC").second,
            time_zone=str(pendulum.now("UTC").tz)
        ))
    )

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/msp_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )


@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_for_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.msp.pl.read_database")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.msp.logger")
@freeze_time("2025-04-30 00:00:00 UTC")
def test_transform_data(
    fake_logger,
    fake_get_station_list,
    fake_check_for_new_stations
):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/msp_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = MspPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where __downloaded_data is empty
    with pytest.raises(RuntimeError, match=f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Starting Transformation for {pipeline.name}")
    fake_logger.error.assert_called_once_with(f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting")

    # Clean Up
    fake_logger.reset_mock()

    # Assign dict a value so that it doesn't get seen as empty
    pipeline._EtlPipeline__downloaded_data["msp"] = pl.LazyFrame()

    # Case where transformation block fails:
    with pytest.raises(RuntimeError, match=rf"Error when trying to transform the data for {pipeline.name}.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting Transformation for {pipeline.name}")
    fake_logger.error.assert_any_call(Contains(f"Error when trying to transform the data for {pipeline.name}."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Actually populate the __downloaded_data
    pipeline._EtlPipeline__downloaded_data["msp"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/msp_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=MSP_DTYPE_SCHEMA["msp"]
    )

    # Case where fake_check_for_new_stations fails
    fake_check_for_new_stations.side_effect = Exception("Error")

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting Transformation for {pipeline.name}")
    fake_logger.error.assert_called_once_with(f"Error when trying to check for new stations. Continuing without checking")
    fake_logger.info.assert_any_call((f"Transformation of {pipeline.name} complete"))

    # Clean Up
    fake_check_for_new_stations.reset_mock(side_effect=True)
    fake_logger.reset_mock()

    # Case where new station is found
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id": ["new_station"]})

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting Transformation for {pipeline.name}")
    fake_logger.warning.assert_called_once_with(Contains("NOTICE: New stations for manual snow survey found. Please go to the following link with new stations IDs"))
    fake_logger.info.assert_any_call((f"Transformation of {pipeline.name} complete"))

    # Clean Up
    fake_check_for_new_stations.reset_mock(side_effect=True)
    fake_logger.reset_mock()

    # Case where no new station is found as well as the happy case
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id": []})

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting Transformation for {pipeline.name}")
    fake_logger.info.assert_any_call("No new stations found. Moving on to transformation")
    fake_logger.info.assert_any_call((f"Transformation of {pipeline.name} complete"))

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"msp"}
    assert pipeline._EtlPipeline__transformed_data["msp"]["pkey"] == ["station_id", "survey_period", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["msp"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["msp"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/msp_output.csv",
                has_header=True,
                null_values=[""],
                schema_overrides={
                    'station_id': pl.Int64,
                    'variable_id': pl.Int32,
                    'survey_period': pl.Date,
                    'datestamp': pl.Date,
                    'value': pl.Float64,
                    'code': pl.String,
                    'qa_id': pl.Int32
                }
            )
        )
    )
