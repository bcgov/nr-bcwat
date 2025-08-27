from etl_pipelines.scrapers.StationObservationPipeline.climate.flnro_wmb import FlnroWmbPipeline
from etl_pipelines.utils.constants import(
    ENV_FLNRO_WMB_BASE_URL,
    ENV_FLNRO_WMB_DESTINATION_TABLES,
    ENV_FLNRO_WMB_DTYPE_SCHEMA,
    ENV_FLNRO_WMB_MIN_RATIO,
    ENV_FLNRO_WMB_NAME,
    ENV_FLNRO_WMB_NETWORK_ID,
    ENV_FLNRO_WMB_RENAME_DICT,
    ENV_FLNRO_WMB_STATION_SOURCE,
    NEW_STATION_MESSAGE_FRAMEWORK
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch
import polars as pl
import polars.testing as plt
import pendulum
import pytest

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.flnro_wmb.pl.read_database")
@freeze_time("2025-08-27 00:00:00 UTC")
def test_initialization(mock_get_station_list):
    # Set up mocks
    mock_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flnro_wmb_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlnroWmbPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Populate expected source_url
    date_list = [pendulum.now("UTC").subtract(days=x) for x in range(3)]
    expected_source_url = {date.strftime("%Y-%m-%d"): ENV_FLNRO_WMB_BASE_URL.format(date.year, date.strftime("%Y-%m-%d")) for date in date_list}
    # Assertion time
    assert pipeline.name == ENV_FLNRO_WMB_NAME
    assert pipeline.source_url == expected_source_url
    assert pipeline.destination_tables == ENV_FLNRO_WMB_DESTINATION_TABLES
    assert pipeline.days == 3
    assert pipeline.station_source == ENV_FLNRO_WMB_STATION_SOURCE
    assert pipeline.expected_dtype == ENV_FLNRO_WMB_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == ENV_FLNRO_WMB_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == ENV_FLNRO_WMB_NETWORK_ID
    assert pipeline.min_ratio == ENV_FLNRO_WMB_MIN_RATIO
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
        pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flnro_wmb_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )
    )


    assert True

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_for_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.flnro_wmb.pl.read_database")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.flnro_wmb.logger")
def test_transform_data(
    fake_logger,
    fake_get_station_list,
    fake_check_for_new_stations
):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flnro_wmb_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlnroWmbPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # No downloaded data case
    with pytest.raises(RuntimeError, match=f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.error.assert_any_call(f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting")
    fake_logger.debug.assert_not_called()
    fake_logger.warning.assert_not_called()

    # Clean up
    fake_logger.reset_mock()

    # Fail checking for new station case
    ## Set the value __downloaded_data value to exist
    pipeline._EtlPipeline__downloaded_data["station_data"] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/flnro_wmb_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=ENV_FLNRO_WMB_DTYPE_SCHEMA["station_data"]
        )
    )

    ## Set fake_check_for_new_stations to raise exception
    fake_check_for_new_stations.side_effect = Exception("error")

    pipeline.transform_data()

    # Only going to check that the correct logs were logged
    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.error.assert_any_call(f"Failed to get new stations from the data downloaded for {pipeline.name}. Moving on without inserting new stations.")
    fake_logger.debug.assert_any_call("Starting Transformation")
    fake_logger.error.assert_called_once()

    # Clean up
    fake_logger.reset_mock()
    fake_check_for_new_stations.reset_mock(side_effect=True)

    # No new stations were found case
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id": []})

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.info.assert_any_call(f"There are no new stations in the data downloaded for {pipeline.name}. Continuing on")
    fake_logger.debug.assert_any_call("Starting Transformation")
    fake_logger.error.assert_not_called()
    fake_logger.warning.assert_not_called()

    # Clean Up
    fake_logger.mock_reset()

    # New station found case
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id":["new_station", "4793"]})

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.warning.assert_any_call(
        NEW_STATION_MESSAGE_FRAMEWORK.format(
            ENV_FLNRO_WMB_NAME,
            "new_station",
            "BC Government: Ministry of Forests",
            "Please check that the stations are within BC before inserting.",
            ENV_FLNRO_WMB_NAME,
            ", ".join(ENV_FLNRO_WMB_NETWORK_ID)
        )
    )
    fake_logger.debug.assert_any_call("Starting Transformation")
    fake_logger.error.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id": []})

    # Transformation Failure case
    pipeline._EtlPipeline__downloaded_data["station_data"] = (
        pl.LazyFrame({"original_id":[]})
    )

    with pytest.raises(RuntimeError, match=rf"Error when trying to transform the data for {pipeline.name}.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.info.assert_any_call(f"There are no new stations in the data downloaded for {pipeline.name}. Continuing on")
    fake_logger.debug.assert_any_call("Starting Transformation")
    fake_logger.error.assert_called_once()

    # Clean UP
    fake_logger.reset_mock()

    # Success case
    pipeline._EtlPipeline__downloaded_data["station_data"] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/flnro_wmb_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=ENV_FLNRO_WMB_DTYPE_SCHEMA["station_data"]
        )
    )

    pipeline.transform_data()
    pipeline._EtlPipeline__transformed_data["station_data"]["df"].write_csv("etl_pipelines/tests/test_constants/station_csv/flnro_wmb_output.csv", quote_style="always")

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.info.assert_any_call(f"There are no new stations in the data downloaded for {pipeline.name}. Continuing on")
    fake_logger.debug.assert_any_call("Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")
    fake_logger.error.assert_not_called()

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data) == {"station_data"}
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/flnro_wmb_output.csv",
                has_header=True,
                schema_overrides={
                    "station_id": pl.Int64,
                    "datestamp": pl.Date,
                    "qa_id": pl.Int32,
                    "variable_id": pl.Int32,
                    "value": pl.Float64
                }
            )
        ),
        check_row_order=False,
        check_column_order=False
    )
