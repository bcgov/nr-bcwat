from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.climate_ec_update import QuarterlyEcUpdatePipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_EC_BASE_URL,
    QUARTERLY_EC_DESTINATION_TABLES,
    QUARTERLY_EC_DTYPE_SCHEMA,
    QUARTERLY_EC_MIN_RATIO,
    QUARTERLY_EC_NAME,
    QUARTERLY_EC_NETWORK_ID,
    QUARTERLY_EC_RENAME_DICT,
    QUARTERLY_EC_STATION_SOURCE
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

@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.climate_ec_update.pl.read_database")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_initialization(fake_get_station_list):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = QuarterlyEcUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    assert pipeline.name == QUARTERLY_EC_NAME
    assert pipeline.source_url == {
        '1012475_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1012475_2025_P1D.csv',
        '1125852_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1125852_2025_P1D.csv',
        '1108395_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1108395_2025_P1D.csv',
        '1017254_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1017254_2025_P1D.csv',
        '1114619_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1114619_2025_P1D.csv',
        '1054503_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1054503_2025_P1D.csv',
        '1037553_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1037553_2025_P1D.csv',
        '1086082_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1086082_2025_P1D.csv',
        '1017230_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1017230_2025_P1D.csv',
        '1085836_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1085836_2025_P1D.csv',
        '114B1F0_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_114B1F0_2025_P1D.csv',
        '1037090_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1037090_2025_P1D.csv',
        '1064324_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1064324_2025_P1D.csv',
        '119BLM0_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_119BLM0_2025_P1D.csv',
        '1161662_2025': 'https://dd.meteo.gc.ca/20250828/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_1161662_2025_P1D.csv'
    }
    assert pipeline.destination_tables == QUARTERLY_EC_DESTINATION_TABLES
    assert pipeline.days == 92
    assert pipeline.station_source == QUARTERLY_EC_STATION_SOURCE
    assert pipeline.expected_dtype == QUARTERLY_EC_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == QUARTERLY_EC_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == QUARTERLY_EC_NETWORK_ID
    assert pipeline.min_ratio == QUARTERLY_EC_MIN_RATIO
    assert pipeline.file_encoding == "utf8-lossy"
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
            year=pendulum.now("UTC").subtract(days=92).year,
            month=pendulum.now("UTC").subtract(days=92).month,
            day=pendulum.now("UTC").subtract(days=92).day,
            hour=pendulum.now("UTC").subtract(days=92).hour,
            second=pendulum.now("UTC").subtract(days=92).second,
            time_zone=str(pendulum.now("UTC").subtract(days=92).tz)
        ))
    )

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
    )
    )

@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.climate_ec_update.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.climate_ec_update.logger")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_transform_data(
    fake_logger,
    fake_get_station_list
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = QuarterlyEcUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Empty __downloaded_data case
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame()

    with pytest.raises(RuntimeError, match="No data was found in the attribute self._EtlPipeline__downloaded_data! Exiting with failure."):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Starting trasformation for {pipeline.name}")
    fake_logger.error.assert_called_once_with("No data was found in the attribute self._EtlPipeline__downloaded_data! Exiting with failure.")

    # Clean Up
    fake_logger.reset_mock()

    # Fails in transformation case
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame({"original_id": ["failure"]})

    with pytest.raises(RuntimeError, match=rf"Failed to transform data for {pipeline.name}."):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Starting trasformation for {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains(f"Failed to transform data for {pipeline.name}. Exiting with failure."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Successful Case
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=QUARTERLY_EC_DTYPE_SCHEMA["station_data"]
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation for {pipeline.name}")
    fake_logger.info.assert_any_call(f"Finished transforming data for {pipeline.name}")
    fake_logger.error.assert_not_called()

    assert fake_logger.info.call_count == 2
    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"station_data"}
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_output.csv",
            has_header=True,
            null_values=[""],
            schema_overrides={
                'station_id': pl.Int64,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'qa_id': pl.Int32
            }
        )
    )
    assert True
