from etl_pipelines.scrapers.StationObservationPipeline.water.flow_works import FlowWorksPipeline
from etl_pipelines.utils.constants import(
    FLOWWORKS_DESTINATION_TABLE,
    FLOWWORKS_DTYPE_SCHEMA,
    FLOWWORK_MIN_RATIO,
    FLOWWORKS_NAME,
    FLOWWORKS_NETWORK,
    FLOWWORKS_RENAME_DICT,
    FLOWWORKS_STATION_SOURCE,
    FLOWWORKS_BASE_URL,
    FLOWWORKS_IDEAL_VARIABLES,
    FLOWWORKS_TOKEN_URL,
    HEADER
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch, PropertyMock, MagicMock
from callee import Contains
import polars as pl
import polars.testing as plt
import pendulum
import pytest
import json

@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_initialization(
    fake_get_station_list
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/env_hydro_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == FLOWWORKS_NAME
    assert pipeline.source_url == FLOWWORKS_BASE_URL
    assert pipeline.destination_tables == FLOWWORKS_DESTINATION_TABLE
    assert pipeline.days == 2
    assert pipeline.station_source == FLOWWORKS_STATION_SOURCE
    assert pipeline.expected_dtype == FLOWWORKS_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == FLOWWORKS_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == FLOWWORKS_NETWORK
    assert pipeline.min_ratio == FLOWWORK_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)
    assert pipeline.variable_to_scrape == {}
    assert pipeline.auth_header == HEADER

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/env_hydro_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__find_ideal_variables")
@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_station_data")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.time.sleep")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.requests.get")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_download_data(
    fake_get_station_list,
    fake_logger,
    fake_get,
    no_sleep,
    fake_get_station_data,
    fake_ideal_vars
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/env_hydro_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where __get_flowworks_station_data fails
    fake_get_station_data.side_effect = Exception("Error")

    with pytest.raises(Exception, match=r".*Error.*"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with("Getting all station metadata from the FlowWorks API")

    # Clean Up
    fake_logger.reset_mock()
    fake_get_station_data.reset_mock(side_effect=True)

    # Case where __find_ideal_variables fails
    fake_get_station_data.return_value = pl.LazyFrame({"original_id": ["test_id"]})
    fake_ideal_vars.side_effect = Exception("Error")

    if FLOWWORK_MIN_RATIO > 0:
        with pytest.raises(RuntimeError, match=rf"More than {pipeline.min_ratio * 100} of the data was not downloaded.*"):
            pipeline.download_data()

        fake_logger.error.assert_any_call(Contains("Failed to find ideal variables, there may have been an key mismatch."))
        fake_logger.error.assert_any_call(f"More than {pipeline.min_ratio * 100} of the data was not downloaded, exiting")
    else:
        pipeline.download_data()
        fake_logger.error.assert_called_once_with(Contains("Failed to find ideal variables, there may have been an key mismatch."))
        fake_logger.info.assert_any_call(f"Fishined downloading data for {pipeline.name}")

    fake_logger.info.assert_any_call("Getting all station metadata from the FlowWorks API")
    fake_logger.debug.assert_called_once_with("Downloading data for station test_id")
    fake_logger.warning.assert_any_call(f"Failed to find ideal variables, will retry")

    assert fake_logger.warning.call_count == 3
    assert pipeline._EtlPipeline__download_num_retries == 3

    # Clean Up
    fake_logger.reset_mock()
    fake_ideal_vars.reset_mock(side_effect=True)

    # Case where data download fails
    pipeline.variable_to_scrape = []

    if FLOWWORK_MIN_RATIO > 0:
        with pytest.raises(RuntimeError, match=rf"More than {pipeline.min_ratio * 100} of the data was not downloaded.*"):
            pipeline.download_data()

        fake_logger.error.assert_any_call(Contains("An error occurred while trying to download data for station_id"))
        fake_logger.error.assert_any_call(f"More than {pipeline.min_ratio * 100} of the data was not downloaded, exiting")
    else:
        pipeline.download_data()
        fake_logger.error.assert_called_once_with(Contains("An error occurred while trying to download data for station_id"))
        fake_logger.info.assert_any_call(f"Fishined downloading data for {pipeline.name}")

    fake_logger.info.assert_any_call("Getting all station metadata from the FlowWorks API")
    fake_logger.debug.assert_any_call("Downloading data for station test_id")
    fake_logger.debug.assert_any_call("Getting data from API for each variable that found it's best match")

    # Clean Up
    fake_logger.reset_mock()

    # Case where there is no variable_to_scrape
    pipeline.variable_to_scrape = {"discharge": None}

    pipeline.download_data()

    fake_logger.info.assert_any_call("Getting all station metadata from the FlowWorks API")
    fake_logger.debug.assert_any_call("Downloading data for station test_id")
    fake_logger.debug.assert_any_call("Getting data from API for each variable that found it's best match")
    fake_logger.warning.assert_called_once_with(Contains("There was no data to be scraped for any variables for station ID"))
    fake_logger.info.assert_any_call(f"Fishined downloading data for {pipeline.name}")

    # Clean Up
    fake_logger.reset_mock()

    # Case when requests.get doesn't return status code 200
    pipeline.variable_to_scrape = {"discharge": 1}

    status_code = PropertyMock(return_value = 404)
    fake_response = MagicMock()

    fake_get.return_value = fake_response
    type(fake_response).status_code = status_code

    if FLOWWORK_MIN_RATIO > 0:
        with pytest.raises(RuntimeError, match=rf"More than {pipeline.min_ratio * 100} of the data was not downloaded.*"):
            pipeline.download_data()

        fake_logger.error.assert_any_call(Contains("Failed when downloading data from the FlowWorks API."))
        fake_logger.error.assert_any_call(f"More than {pipeline.min_ratio * 100} of the data was not downloaded, exiting")
    else:
        pipeline.download_data()

        fake_logger.info.assert_any_call(f"Fishined downloading data for {pipeline.name}")
        fake_logger.error.assert_called_once_with(Contains("Failed when downloading data from the FlowWorks API."))


    fake_logger.info.assert_any_call("Getting all station metadata from the FlowWorks API")
    fake_logger.debug.assert_any_call("Downloading data for station test_id")
    fake_logger.debug.assert_any_call("Getting data from API for each variable that found it's best match")
    fake_logger.warning.assert_called()

    assert fake_logger.warning.call_count == 3

    # Clean Up
    fake_logger.reset_mock()

    # Case where the retrieved data is empty
    status_code = PropertyMock(return_value = 200)
    type(fake_response).status_code = status_code

    fake_response.json.return_value = json.loads('{"Resources": [], "ResultCode": 0, "ResultMessage": "Request OK – Request is valid and was accepted."}')

    if FLOWWORK_MIN_RATIO > 0:
        with pytest.raises(RuntimeError, match=rf"More than {pipeline.min_ratio * 100} of the data was not downloaded.*"):
            pipeline.download_data()

        fake_logger.error.assert_any_call(f"More than {pipeline.min_ratio * 100} of the data was not downloaded, exiting")
    else:
        pipeline.download_data()

        fake_logger.info.assert_any_call(f"Fishined downloading data for {pipeline.name}")

    fake_logger.info.assert_any_call("Getting all station metadata from the FlowWorks API")
    fake_logger.debug.assert_any_call("Downloading data for station test_id")
    fake_logger.debug.assert_any_call("Getting data from API for each variable that found it's best match")
    fake_logger.warning.assert_called_once_with(Contains(f"Did not find any data in the response for discharge."))

    # Clean Up
    fake_logger.reset_mock()

    # Success Case
    fake_response.json.return_value = json.loads('{"Resources": [{"DataValue": "22.22", "DateTime": "2025-09-03T00:00:00"}, {"DataValue": "35.35", "DateTime": "2025-09-02T12:00:00"}], "ResultCode": 0, "ResultMessage": "Request OK – Request is valid and was accepted."}')

    pipeline.download_data()

    fake_logger.info.assert_any_call("Getting all station metadata from the FlowWorks API")
    fake_logger.debug.assert_any_call("Downloading data for station test_id")
    fake_logger.debug.assert_any_call("Getting data from API for each variable that found it's best match")
    fake_logger.info.assert_any_call(f"Fishined downloading data for {pipeline.name}")

    fake_logger.warning.assert_not_called()
    fake_logger.error.assert_not_called()



def test_transform_data():
    assert True
