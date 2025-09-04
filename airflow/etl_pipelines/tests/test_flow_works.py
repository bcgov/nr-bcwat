from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.scrapers.StationObservationPipeline.water.flow_works import FlowWorksPipeline
from etl_pipelines.scrapers.EtlPipeline import EtlPipeline
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
import os

@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_initialization(
    fake_get_station_list,
    fake_token
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
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
            "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

    fake_token.assert_called_once()

@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
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
    fake_ideal_vars,
    fake_token
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
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
    fake_response.json.return_value = json.loads('{"Resources": [{"Name": "22.22", "DateTime": "2025-09-03T00:00:00"}, {"DataValue": "35.35", "DateTime": "2025-09-02T12:00:00"}], "ResultCode": 0, "ResultMessage": "Request OK – Request is valid and was accepted."}')

    pipeline.download_data()

    fake_logger.info.assert_any_call("Getting all station metadata from the FlowWorks API")
    fake_logger.debug.assert_any_call("Downloading data for station test_id")
    fake_logger.debug.assert_any_call("Getting data from API for each variable that found it's best match")
    fake_logger.info.assert_any_call(f"Fishined downloading data for {pipeline.name}")

    fake_logger.warning.assert_not_called()
    fake_logger.error.assert_not_called()

@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_transform_data(
    fake_get_station_list,
    fake_logger,
    fake_token
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    #Case where it fails because no downloaded data

    with pytest.raises(ValueError, match="No data exists in the _EtlPipeline__downloaded_data attribute! Expected at least a little."):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with("Starting transformation for FlowWorks pipeline")
    fake_logger.error.assert_called_once_with(Contains("No data was downloaded to be transformed for the CRD FlowWorks pipeline."))

    # Clean Up
    fake_logger.reset_mock()

    # Case where it fails in the transformation block
    pipeline._EtlPipeline__downloaded_data = {
        "discharge": pl.LazyFrame()
    }

    with pytest.raises(RuntimeError, match=r"There was an error when trying to transform the data for discharge.*"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with("Starting transformation for FlowWorks pipeline")
    fake_logger.error.assert_called_once_with(Contains(f"There was an error when trying to transform the data for discharge."))

    # Clean Up
    fake_logger.reset_mock()

    # Success Case
    pipeline._EtlPipeline__downloaded_data = {
        "discharge": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/flowworks_discharge_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=FLOWWORKS_DTYPE_SCHEMA["discharge"]
        ),
        "stage": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/flowworks_stage_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=FLOWWORKS_DTYPE_SCHEMA["stage"]
        ),
        "swe": pl.LazyFrame(schema={
            "DataValue": pl.Float64,
            "DataTime": pl.String,
            "original_id": pl.Int32
        }),
        "pc": pl.LazyFrame(schema={
            "DataValue": pl.Float64,
            "DataTime": pl.String,
            "original_id": pl.Int32
        }),
        "rainfall": pl.LazyFrame(schema={
            "DataValue": pl.Float64,
            "DataTime": pl.String,
            "original_id": pl.Int32
        }),
        "temperature": pl.LazyFrame(schema={
            "DataValue": pl.Float64,
            "DataTime": pl.String,
            "original_id": pl.Int32
        })
    }

    pipeline.transform_data()

    fake_logger.info.assert_any_call("Starting transformation for FlowWorks pipeline")
    fake_logger.info.assert_any_call(f"Finished transforming downloaded data for {pipeline.name}")
    fake_logger.warning.assert_not_called()
    fake_logger.error.assert_not_called()

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"station_data"}
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/flowworks_output.csv",
            has_header=True,
            null_values=[""],
            schema_overrides={
                'station_id': pl.Int64,
                'datestamp': pl.Date,
                'value': pl.Float64,
                'qa_id': pl.Int32,
                'variable_id': pl.Int32
            }
        ),
        check_column_order=False,
        check_row_order=False
    )

@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
@patch.object(EtlPipeline, "validate_downloaded_data")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_validate_downloaded_data(
    fake_get_station_list,
    fake_logger,
    fake_validation,
    fake_token
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where there is no data in __downloaded_data
    with pytest.raises(ValueError, match="No data exists in the _EtlPipeline__downloaded_data attribute! Expected at least a little."):
        pipeline.validate_downloaded_data()

    fake_logger.error.assert_called_once_with("No data was downloaded to be validated for the FlowWorks pipeline. This is not expected since it includes the CRD FlowWorks Pipeline.")

    # Clean Up
    fake_logger.reset_mock()

    # Success Case
    pipeline._EtlPipeline__downloaded_data["discharge"] = pl.LazyFrame()

    pipeline.validate_downloaded_data()

    for key in pipeline.expected_dtype.keys():
        assert pipeline.expected_dtype[key]["original_id"] == pl.Int32

    fake_validation.assert_called_once()


@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
@patch.object(EtlPipeline, "load_data")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_load_data(
    fake_get_station_list,
    fake_logger,
    fake_load,
    fake_token
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where there is no data in __transformed_data
    with pytest.raises(ValueError, match="No data exists in the _EtlPipeline__transformed_data attribute! Expected at least a little."):
        pipeline.load_data()

    fake_logger.error.assert_called_once_with("No data was transformed to be loaded on to the database for the FlowWorks pipeline. This is not expected since it includes the CRD FlowWorks Pipeline.")

    # Clean Up
    fake_logger.reset_mock()

    # Success Case
    pipeline._EtlPipeline__transformed_data["discharge"] = pl.LazyFrame()

    pipeline.load_data()

    fake_load.assert_called_once()


@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.requests.post")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_get_flowworks_token(
    fake_get_station_list,
    fake_logger,
    fake_post
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Case where one of the env vars are not set
    # Set ENV vars
    os.environ["FLOWWORKS_USER"] = "TEST_USER"
    os.environ["FLOWWORKS_PASS"] = ""

    # Initialize Pipeline
    with pytest.raises(ValueError, match=r"FlowWorks credentials were not found in the environment variables.*"):
        pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    fake_logger.error.assert_called_once_with("FlowWorks credentials were not found in the environment variables.")

    # Clean up
    fake_logger.reset_mock()
    os.environ["FLOWWORKS_PASS"] = "TEST_PASS"

    # Case where requests.post fails
    fake_post.side_effect = Exception("Error")

    with pytest.raises(ValueError, match=r"There was an error trying to get the FlowWorks Authorization token .*Error.*"):
        pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    fake_logger.error.assert_called_once_with(Contains("There was an error trying to get the FlowWorks Authorization token"))

    # Clean Up
    fake_logger.reset_mock()
    fake_post.reset_mock(side_effect=True)

    # Case where status_code is not 200
    fake_response = MagicMock()
    status_code = PropertyMock(return_value=505)
    fake_post.return_value = fake_response
    type(fake_response).status_code = status_code

    with pytest.raises(ValueError, match=r"There was an error trying to get the FlowWorks Authorization token .*Post request for Auth token did not have status code 200!.*"):
        pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    fake_logger.error.assert_called_once_with(Contains("There was an error trying to get the FlowWorks Authorization token"))

    # Clean Up
    fake_logger.reset_mock()

    # Success
    status_code = PropertyMock(return_value = 200)
    type(fake_response).status_code = status_code
    fake_response.json.return_value = "GriGri"

    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    fake_response.json.assert_called_once()
    fake_logger.assert_not_called()

    assert pipeline.auth_header["Authorization"] == "Bearer GriGri"

@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_check_api_request_response(
    fake_get_station_list,
    fake_logger,
    fake_token
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Catch KeyError
    with pytest.raises(RuntimeError, match=r"Scraping for flowworks failed as the API response did not contain the key.*"):
        pipeline._FlowWorksPipeline__check_api_request_response(response={})

    fake_logger.error.assert_called_once_with(Contains("Scraping for flowworks failed as the API response did not contain the key"))

    # Clean Up
    fake_logger.reset_mock()

    # ResultCode is not 0
    with pytest.raises(RuntimeError, match=r"Scraping for flowworks failed as the API ResultCode was not 0!.*"):
        pipeline._FlowWorksPipeline__check_api_request_response(response={"ResultCode": 1})

    fake_logger.error.assert_called_once_with(Contains("Scraping for flowworks failed as the API ResultCode was not 0!"))

    # Clean Up
    fake_logger.reset_mock()

    # ResultMessage Not pass
    with pytest.raises(RuntimeError, match=r"Scraping for flowworks failed as the API ResultMessage was not 'Request OK'!.*"):
        pipeline._FlowWorksPipeline__check_api_request_response(response={"ResultCode": 0, "ResultMessage": "Failed"})

    fake_logger.error.assert_called_once_with(Contains("Scraping for flowworks failed as the API ResultMessage was not 'Request OK'!"))

    # Clean Up
    fake_logger.reset_mock()

    # Success
    pipeline._FlowWorksPipeline__check_api_request_response(response={"ResultCode": 0, "ResultMessage": "Request OK – Request is valid and was accepted."})

    fake_logger.assert_not_called()

@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__check_api_request_response")
@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.requests.get")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_find_ideal_variables(
    fake_get_station_list,
    fake_logger,
    fake_get,
    fake_token,
    fake_check_api
):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # requests.get fails
    fake_get.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=rf"Failed to get station metadata from the url:.*"):
        pipeline._FlowWorksPipeline__find_ideal_variables(url="test_url.com")

    fake_logger.error.assert_called_once_with(Contains(f"Failed to get station metadata from the url: test_url.com."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_get.reset_mock(side_effect=True)

    # status_code not 200
    status_code = PropertyMock(return_value=404)
    fake_response = MagicMock()
    fake_get.return_value = fake_response
    type(fake_response).status_code = status_code

    with pytest.raises(RuntimeError, match=r"Request status code was not 200!.*"):
        pipeline._FlowWorksPipeline__find_ideal_variables(url="test_url.com")

    fake_logger.error.assert_called_once_with(Contains(f"Request status code was not 200!"))

    #Clean Up
    fake_logger.reset_mock()

    # __check_api_request_response fails
    fake_check_api.side_effect = RuntimeError("Error")
    status_code = PropertyMock(return_value = 200)
    type(fake_response).status_code = status_code

    with pytest.raises(RuntimeError, match=r"Got 200 response from API but failed to check for errors.*"):
        pipeline._FlowWorksPipeline__find_ideal_variables(url="test_url.com")

    fake_logger.error.assert_called_once_with(Contains(f"Got 200 response from API but failed to check for errors."))

    #Clean Up
    fake_logger.reset_mock()
    fake_check_api.reset_mock(side_effect=True)

    # Success
    fake_response.json.return_value = json.loads('{"Resources": [{"Name": "Preliminary Discharge", "Id": "1"}, {"Name": "Temperature", "Id": "1"}], "ResultCode": 0, "ResultMessage": "Request OK – Request is valid and was accepted."}')

    pipeline._FlowWorksPipeline__find_ideal_variables(url="test_url.com")

    fake_logger.info.assert_called_once_with("Finding ideal variables from FlowWorks Channels")

    assert len(pipeline.variable_to_scrape.keys()) == 6
    assert set(pipeline.variable_to_scrape.keys()) == {"discharge", "stage", "swe", "pc", "rainfall", "temperature"}

    for key in pipeline.variable_to_scrape.keys():
        if key in ["discharge", "temperature"]:
            assert pipeline.variable_to_scrape[key] == "1"
        else:
            assert pipeline.variable_to_scrape[key] == None


@patch.object(StationObservationPipeline, "insert_new_stations")
@patch.object(StationObservationPipeline, "construct_insert_tables")
@patch.object(StationObservationPipeline, "check_new_station_in_bc")
@patch.object(StationObservationPipeline, "check_for_new_stations")
@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__find_ideal_variables")
@patch.object(FlowWorksPipeline, "_FlowWorksPipeline__get_flowworks_token")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.flow_works.pl.read_database")
@freeze_time("2025-09-03 00:00:00 UTC")
def test_get_and_insert_new_stations(
    fake_get_station_list,
    fake_logger,
    fake_token,
    fake_ideal_vars,
    fake_check_station,
    fake_check_in_bc,
    fake_construct,
    fake_insert_station

):
    # Set up fakes
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/flowworks_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = FlowWorksPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where check_for_new_stations fails
    fake_check_station.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to check for new stations.*"):
        pipeline.get_and_insert_new_stations(pl.LazyFrame({"Id": [100]}))

    fake_logger.error.assert_called_once_with(Contains(f"Failed to check for new stations."))

    # Clean Up
    fake_logger.reset_mock()
    fake_check_station.reset_mock(side_effect=True)

    # check_for_new_stations succeeds but not new stations
    fake_check_station.return_value = pl.LazyFrame()

    pipeline.get_and_insert_new_stations(pl.LazyFrame({"Id": [100]}))

    fake_logger.info.assert_called_once_with("No new stations found, going back to transformation")

    # Clean Up
    fake_logger.reset_mock()

    # Case where after removing stations with "Demo" in name, or Blank Longitude, or Latitude, there are no stations
    fake_check_station.return_value = pl.LazyFrame({"original_id": ["HRB100", "HRB200"]})

    pipeline.get_and_insert_new_stations(pl.LazyFrame({
        "Id": [100, 200],
        "Name": ["test_stations", "Demo_station"],
        "Longitude": ["", "-121.023092"],
        "Latitude": ["54.1298", "-110.239829"]
    }))

    fake_logger.info.assert_called_once_with("No new stations that are not Demo stations, or stations without Lat, Lon were found. Going back to transformation")

    # Case where check_new_station_in_bc fails
    fake_check_station.return_value = pl.LazyFrame({"original_id": ["HRB100", "HRB200", "HRB300"]})
    fake_check_in_bc.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to check if new stations are in BC.*"):
        pipeline.get_and_insert_new_stations(pl.LazyFrame({
        "Id": [100, 200, 300],
        "Name": ["test_station", "Demo_station", "not_in_bc"],
        "Longitude": ["", "-121.023092", "110.3230"],
        "Latitude": ["54.1298", "-110.239829", "-32.928938"]
    }))

    fake_logger.error.assert_called_once_with(Contains(f"Failed to check if new stations are in BC"))

    # Clean Up
    fake_logger.reset_mock()
    fake_check_in_bc.reset_mock(side_effect=True)

    # check_for_new_stations succeeds but not new stations
    fake_check_in_bc.return_value = []

    pipeline.get_and_insert_new_stations(pl.LazyFrame({
        "Id": [100, 200, 300],
        "Name": ["test_station", "Demo_station", "not_in_bc"],
        "Longitude": ["", "-121.023092", "110.3230"],
        "Latitude": ["54.1298", "-110.239829", "-32.928938"]
    }))

    fake_logger.info.assert_called_once_with("No new stations found in BC, going back to transformation")

    # Clean Up
    fake_logger.reset_mock()
    fake_check_station.return_value = pl.LazyFrame({"original_id": ["HRB100", "HRB200", "HRB300", "HRB400", "HRB500"]})
    fake_check_in_bc.return_value = ["HRB400", "HRB500"]

    # Case where __find_ideal_variables fails
    fake_ideal_vars.side_effect = Exception("Error")

    pipeline.get_and_insert_new_stations(pl.LazyFrame({
        "Id": [100, 200, 300, 400, 500],
        "Name": ["test_station", "Demo_station", "not_in_bc", "new_station1", "new_station2"],
        "Longitude": ["", "-121.023092", "110.3230", "-124.92938", "-123.02389"],
        "Latitude": ["54.1298", "-110.239829", "-32.928938", "54.1928302", "55.912839"]
    }))

    fake_logger.warning.assert_any_call(Contains("Getting Ideal Variables failed for"))
    fake_logger.warning.assert_any_call("There were no stations that had any variable_id's or station_type. Exiting out to transformation")

    assert fake_logger.warning.call_count == 3

    # Clean Up
    fake_logger.reset_mock()
    fake_ideal_vars.reset_mock(side_effect=True)

    # Case Where it __find_ideal_variables doesn't fail, but construct_insert_tables does
    pipeline.variable_to_scrape = {
        "discharge": 1,
        "stage": 1,
        "temperature": None,
        "rainfall": None,
        "swe": None,
        "pc": None
    }
    fake_construct.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Error when trying to construct the insertion dataframes.*"):
        pipeline.get_and_insert_new_stations(pl.LazyFrame({
            "Id": [100, 200, 300, 400, 500],
            "Name": ["test_station", "Demo_station", "not_in_bc", "new_station1", "new_station2"],
            "Longitude": ["", "-121.023092", "110.3230", "-124.92938", "-123.02389"],
            "Latitude": ["54.1298", "-110.239829", "-32.928938", "54.1928302", "55.912839"]
        }))

    fake_logger.error.assert_called_once_with("Error when trying to construct the insertion dataframes.")

    # Clean Up
    fake_logger.reset_mock()
    fake_construct.reset_mock(side_effect=True)

    # Case where construct_insert_tables succeeds but insert_new_stations fails
    fake_construct.return_value = (pl.LazyFrame(), {})
    fake_insert_station.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Error when trying to insert new stations into the database.*"):
        pipeline.get_and_insert_new_stations(pl.LazyFrame({
            "Id": [100, 200, 300, 400, 500],
            "Name": ["test_station", "Demo_station", "not_in_bc", "new_station1", "new_station2"],
            "Longitude": ["", "-121.023092", "110.3230", "-124.92938", "-123.02389"],
            "Latitude": ["54.1298", "-110.239829", "-32.928938", "54.1928302", "55.912839"]
        }))

    fake_logger.error.assert_called_once_with("Error when trying to insert new stations into the database.")

    # Clean Up
    fake_logger.reset_mock()
    fake_ideal_vars.reset_mock()
    fake_check_station.reset_mock()
    fake_check_in_bc.reset_mock()
    fake_construct.reset_mock()
    fake_insert_station.reset_mock(side_effect=True)

    # Success case
    pipeline.get_and_insert_new_stations(pl.LazyFrame({
            "Id": [100, 200, 300, 400, 500],
            "Name": ["test_station", "Demo_station", "not_in_bc", "new_station1", "new_station2"],
            "Longitude": ["", "-121.023092", "110.3230", "-124.92938", "-123.02389"],
            "Latitude": ["54.1298", "-110.239829", "-32.928938", "54.1928302", "55.912839"]
        }))

    fake_ideal_vars.assert_called()
    fake_check_station.assert_called_once()
    fake_check_in_bc.assert_called_once()
    fake_construct.assert_called_once()
    fake_insert_station.assert_called_once()

    assert fake_ideal_vars.call_count == 2
