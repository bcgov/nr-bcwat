from etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe import GwMoePipeline
from etl_pipelines.utils.constants import(
    MOE_GW_DESTINATION_TABLES,
    MOE_GW_DTYPE_SCHEMA,
    MOE_GW_MIN_RATIO,
    MOE_GW_NAME,
    MOE_GW_NETWORK,
    MOE_GW_RENAME_DICT,
    MOE_GW_STATION_SOURCE,
    QUARTERLY_MOE_GW_DTYPE_SCHEMA,
    QUARTERLY_MOE_GW_MIN_RATIO,
    QUARTERLY_MOE_GW_NAME,
    QUARTERLY_MOE_GW_RENAME_DICT
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

@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
def test_initialization_daily(
    fake_get_station_list
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_gw_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = GwMoePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), quarterly=False)

    # Assertion time
    assert pipeline.name == MOE_GW_NAME
    assert pipeline.source_url == {
        'OW468': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW468-recent.csv',
        'OW467': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW467-recent.csv',
        'OW444': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW444-recent.csv',
        'OW438': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW438-recent.csv',
        'OW268': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW268-recent.csv',
        'OW494': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW494-recent.csv',
        'OW439': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW439-recent.csv',
        'OW236': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW236-recent.csv',
        'OW412': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW412-recent.csv',
        'OW484': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW484-recent.csv',
        'OW240': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW240-recent.csv',
        'OW432': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW432-recent.csv',
        'OW356': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW356-recent.csv',
        'OW478': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW478-recent.csv',
        'OW354': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW354-recent.csv',
        'OW319': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW319-recent.csv',
        'OW401': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW401-recent.csv',
        'OW442': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW442-recent.csv',
        'OW450': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW450-recent.csv',
        'OW118': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW118-recent.csv'
    }
    assert pipeline.destination_tables == MOE_GW_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == MOE_GW_STATION_SOURCE
    assert pipeline.expected_dtype == MOE_GW_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == MOE_GW_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == MOE_GW_NETWORK
    assert pipeline.min_ratio == MOE_GW_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)
    assert pipeline.file_path == "data/"

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/moe_gw_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
def test_initialization_quarterly(
    fake_get_station_list
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_gw_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = GwMoePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), quarterly=True)

    # Assertion time
    assert pipeline.name == QUARTERLY_MOE_GW_NAME
    assert pipeline.source_url == {
        'OW468': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW468-average.csv',
        'OW467': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW467-average.csv',
        'OW444': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW444-average.csv',
        'OW438': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW438-average.csv',
        'OW268': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW268-average.csv',
        'OW494': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW494-average.csv',
        'OW439': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW439-average.csv',
        'OW236': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW236-average.csv',
        'OW412': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW412-average.csv',
        'OW484': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW484-average.csv',
        'OW240': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW240-average.csv',
        'OW432': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW432-average.csv',
        'OW356': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW356-average.csv',
        'OW478': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW478-average.csv',
        'OW354': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW354-average.csv',
        'OW319': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW319-average.csv',
        'OW401': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW401-average.csv',
        'OW442': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW442-average.csv',
        'OW450': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW450-average.csv',
        'OW118': 'http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/OW118-average.csv'
    }
    assert pipeline.destination_tables == MOE_GW_DESTINATION_TABLES
    assert pipeline.days == 365
    assert pipeline.station_source == MOE_GW_STATION_SOURCE
    assert pipeline.expected_dtype == QUARTERLY_MOE_GW_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == QUARTERLY_MOE_GW_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == MOE_GW_NETWORK
    assert pipeline.min_ratio == QUARTERLY_MOE_GW_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=365)

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/moe_gw_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
def test_transform_data(
    fake_get_station_list,
    fake_logger
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_gw_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = GwMoePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), quarterly=False)

    # Case where __downloaded_data is empty
    with pytest.raises(RuntimeError, match="No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Startion Transformation of {pipeline.name}")
    fake_logger.error.assert_called_once_with("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")

    # Clean Up
    fake_logger.reset_mock()

    # Case where __downloaded_data doesn't have correct key
    pipeline._EtlPipeline__downloaded_data["test_key"] = [1]

    with pytest.raises(KeyError, match=r"Error when trying to get the downloaded data from __downloaded_data attribute.*"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Startion Transformation of {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains("Error when trying to get the downloaded data from __downloaded_data attribute."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Case failing in transform block with ColumnNotFoundError
    pipeline._EtlPipeline__downloaded_data = {"station_data": pl.LazyFrame({"myLocation": ["test"]})}

    with pytest.raises(pl.exceptions.ColumnNotFoundError, match=r"Column could not be found or was not expected when transforming groundwater data.*"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Startion Transformation of {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains("Column could not be found or was not expected when transforming groundwater data."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    #Case failing in trasform_block with RuntimeError
    pipeline._EtlPipeline__downloaded_data = {"station_data": pl.DataFrame(schema_overrides=MOE_GW_DTYPE_SCHEMA["station_data"])}

    with pytest.raises(RuntimeError, match=r"Error occured, moste likely due to the fact that the station_list was not a LazyFrame.*"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Startion Transformation of {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains("Error occured, moste likely due to the fact that the station_list was not a LazyFrame."))

    # Clean Up
    fake_logger.reset_mock()

    # Success Case
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_gw_download.csv",
        null_values=[""],
        schema_overrides=MOE_GW_DTYPE_SCHEMA["station_data"]
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Startion Transformation of {pipeline.name}")
    fake_logger.error.asssert_not_called()

    assert len(pipeline._EtlPipeline__transformed_data) == 1
    assert set(pipeline._EtlPipeline__transformed_data) == {"station_data"}
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/moe_gw_output.csv",
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
