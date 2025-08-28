from etl_pipelines.scrapers.StationObservationPipeline.climate.asp import AspPipeline
from etl_pipelines.utils.constants import(
    ASP_BASE_URLS,
    ASP_DESTINATION_TABLES,
    ASP_DTYPE_SCHEMA,
    ASP_MIN_RATIO,
    ASP_NAME,
    ASP_NETWORK,
    ASP_RENAME_DICT,
    ASP_STATION_SOURCE
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

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.asp.pl.read_database")
@freeze_time("2025-08-27 00:00:00 UTC")
def test_initialization(mock_get_station_list):
    # Set up mocks
    mock_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/asp_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = AspPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == ASP_NAME
    assert pipeline.source_url == ASP_BASE_URLS
    assert pipeline.destination_tables == ASP_DESTINATION_TABLES
    assert pipeline.days == 3
    assert pipeline.station_source == ASP_STATION_SOURCE
    assert pipeline.expected_dtype == ASP_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == ASP_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert not pipeline.overrideable_dtype
    assert pipeline.network == ASP_NETWORK
    assert pipeline.min_ratio == ASP_MIN_RATIO
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
            "etl_pipelines/tests/test_constants/station_csv/asp_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_for_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.asp.pl.read_database")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.asp.logger")
@freeze_time("2025-08-27 00:00:00 UTC")
def test_transform_data(
    fake_logger,
    fake_get_station_list,
    fake_check_for_new_stations
):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/asp_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = AspPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

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
    pipeline._EtlPipeline__downloaded_data ={
        "SW": pl.LazyFrame(
            {
                "DATE(UTC)":[],
                "variable": [],
                "value": []
            },
            schema_overrides=ASP_DTYPE_SCHEMA["SW"]
        ),
        "SD": pl.LazyFrame(
            {
                "DATE(UTC)":[],
                "variable": [],
                "value": []
            },
            schema_overrides=ASP_DTYPE_SCHEMA["SW"]
        ),
        "PC": pl.LazyFrame(
            {
                "DATE(UTC)":[],
                "variable": [],
                "value": []
            },
            schema_overrides=ASP_DTYPE_SCHEMA["SW"]
        ),
        "TA": pl.LazyFrame(
            {
                "DATE(UTC)":[],
                "variable": [],
                "value": []
            },
            schema_overrides=ASP_DTYPE_SCHEMA["SW"]
        )
    }

    ## Set fake_check_for_new_stations to raise exception
    fake_check_for_new_stations.side_effect = Exception("error")

    pipeline.transform_data()

    # Only going to check that the correct logs were logged
    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.error.asset_any_call(Contains("Failed to check for new stations in the downloaded data. Continuing on without checking."))
    fake_logger.error.assert_called_once()

    # Clean Up
    fake_logger.reset_mock()

    # Case where transformation fails in the for loop
    pipeline._EtlPipeline__downloaded_data["SW"] = pl.LazyFrame({"variable":[]})

    with pytest.raises(RuntimeError, match=rf"Error when trying to transform the data for {pipeline.name} with SW"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(f"Transforming data for SW")
    fake_logger.error.assert_any_call(Contains(f"Error when trying to transform the data for {pipeline.name} with key SW."),exc_info=True)

    # Clean UP
    fake_logger.reset_mock

    # Fails because the
    # Success case
    pipeline._EtlPipeline__downloaded_data ={
        "SW": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/asp_sw_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=ASP_DTYPE_SCHEMA["SW"]
        ),
        "SD": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/asp_sd_download.csv",
        has_header=True,
            null_values=[""],
            schema_overrides=ASP_DTYPE_SCHEMA["SD"]
        ),
        "PC": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/asp_pc_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=ASP_DTYPE_SCHEMA["PC"]
        ),
        "TA": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/asp_ta_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=ASP_DTYPE_SCHEMA["TA"]
        ),
    }

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Transforming data for SW")
    fake_logger.debug.assert_any_call(f"Transforming data for SD")
    fake_logger.debug.assert_any_call(f"Transforming data for PC")
    fake_logger.debug.assert_any_call(f"Transforming data for TA")
    fake_logger.info.assert_any_call(f"Finished Transformation Step for {pipeline.name}")

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"station_data"}
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/asp_output.csv",
                has_header=True,
                null_values=[""],
                schema_overrides={
                    'datestamp': pl.Date,
                    'station_id': pl.Int64,
                    'variable_id': pl.Int8,
                    'qa_id': pl.Int8,
                    'value': pl.Float64
                }
            )
        ),
        check_column_order=False,
        check_row_order=False
    )
