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
    QUARTERLY_MOE_GW_RENAME_DICT,
    MOE_GW_NEW_STATION_URL
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch, MagicMock, PropertyMock
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
def test_transform_data_daily(
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


@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
def test_transform_data_quarterly(
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
    pipeline = GwMoePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), quarterly=True)

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
        "etl_pipelines/tests/test_constants/station_csv/moe_gw_quarterly_download.csv",
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

    # Make sure that the right qa_id got assigned.
    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"].select("qa_id").unique(),
        pl.DataFrame(
            {"qa_id": [1]},
            schema_overrides={"qa_id": pl.Int8}
        )
    )

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/moe_gw_quarterly_output.csv",
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

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.insert_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.construct_insert_tables")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_new_station_in_bc")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.pl.scan_csv")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.zipfile.ZipFile")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.open")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.sleep")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.requests.get")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
def test_get_and_insert_new_stations(
    fake_get_station_list,
    fake_logger,
    fake_get_request,
    no_sleep,
    fake_open,
    fake_zipfile,
    fake_scan_csv,
    fake_check_new_station_in_bc,
    fake_construct_insert_tables,
    fake_insert_new_stations
):
    # Set up fakes
    fake_get_station_list.return_value = pl.read_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_gw_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    ).lazy()

    no_sleep.return_value = None

    # Initialize Pipeline
    pipeline = GwMoePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), quarterly=False)

    # request.get fails
    fake_get_request.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=rf"Failed to download MOE GW station list from {MOE_GW_NEW_STATION_URL}.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.warning.assert_any_call(f"Error downloading MOE GW station list from URL: {MOE_GW_NEW_STATION_URL}. Retrying...")
    fake_logger.error.assert_called_once_with(Contains(f"Failed to download MOE GW station list from {MOE_GW_NEW_STATION_URL}."), exc_info = True)

    assert fake_logger.warning.call_count == 3
    assert pipeline._EtlPipeline__download_num_retries == 3

    # Clean Up
    fake_logger.reset_mock()
    fake_get_request.reset_mock(side_effect=True)
    pipeline._EtlPipeline__download_num_retries = 0

    # Status Code not 200
    fake_response = MagicMock()
    status_code = PropertyMock(return_value = 404)

    fake_get_request.return_value = fake_response
    type(fake_response).status_code = status_code

    with pytest.raises(RuntimeError, match="Response status was not 200 when trying to download MOE GW station list."):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.warning.assert_any_call(f"Response status was not 200. Retrying...")
    fake_logger.error.assert_called_once_with("Response status was not 200 when trying to download MOE GW station list.")

    assert fake_logger.warning.call_count == 3
    assert pipeline._EtlPipeline__download_num_retries == 3

    # Clean Up
    fake_logger.reset_mock()
    pipeline._EtlPipeline__download_num_retries = 0

    # Fails writing Zipfile
    fake_response = MagicMock()
    status_code = PropertyMock(return_value = 200)

    fake_get_request.return_value = fake_response
    type(fake_response).status_code = status_code
    fake_response.iter_content.return_value = ["Something"]

    fake_open.side_effect = Exception("Error")

    with pytest.raises(IOError, match=r"Failed when trying to write the chunked zipped MOE GW station list file to disk.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.error.assert_called_once_with(Contains("Failed when trying to write the chunked zipped MOE GW station list file to disk."), exc_info = True)

    # Clean Up
    fake_logger.reset_mock()
    fake_open.reset_mock(side_effect=True)

    # Fails extracting zipfile
    fake_open.return_value = MagicMock()
    fake_zipfile.side_effect = Exception("Error")

    with pytest.raises(IOError, match=rf"Failed when trying to unzip the MOE GW station list file.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.error.assert_called_once_with(Contains("Failed when trying to unzip the MOE GW station list file."), exc_info = True)

    # Clean Up
    fake_logger.reset_mock()
    fake_zipfile.reset_mock(side_effect=True)

    # Fails in the checking for new stations block
    fake_scan_csv.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed checking if there were any new stations!.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.debug.assert_any_call(f"Finished Unzipping MOE GW station list")
    fake_logger.error.assert_called_once_with(Contains("Failed checking if there were any new stations!"), exc_info = True)

    # Clean Up
    fake_logger.reset_mock()
    fake_scan_csv.reset_mock(side_effect=True)

    # Case where there is no new stations
    fake_scan_csv.return_value = pl.LazyFrame(
        {
            "observation_well_number": [],
            "obs_well_status_code": []
        },
        schema_overrides={
            "observation_well_number": pl.String,
            "obs_well_status_code": pl.String,
        }
    )

    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.debug.assert_any_call(f"Finished Unzipping MOE GW station list")
    fake_logger.info.assert_any_call(f"No new active stations were found in the station list. Continuing on without inserting.")

    # Clean Up
    fake_logger.reset_mock()

    # Fails Checking if the new station is in BC
    fake_check_new_station_in_bc.side_effect = Exception("Error")
    fake_scan_csv.return_value = pl.LazyFrame(
        {
            "observation_well_number": ["testing"],
            "obs_well_status_code": ["Active"],
            "longitude_Decdeg": ["-121.29392"],
            "latitude_Decdeg": ["53.9384938"],
            "water_supply_system_name": ["Test River"],
            "water_supply_system_well_name": ["Test Well"]
        },
        schema_overrides={
            "observation_well_number": pl.String,
            "obs_well_status_code": pl.String,
            "longitude_Decdeg": pl.String,
            "latitude_Decdeg": pl.String,
            "water_supply_system_name": pl.String,
            "water_supply_system_well_name": pl.String,
        }
    )

    with pytest.raises(RuntimeError, match=r"Failed to check for new stations in BC from the MOE GW station list dataset!.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.debug.assert_any_call(f"Finished Unzipping MOE GW station list")
    fake_logger.error.assert_called_once_with(Contains("Failed to check for new stations in BC from the MOE GW station list dataset!"), exc_info = True)

    # Clean Up
    fake_logger.reset_mock()
    fake_check_new_station_in_bc.reset_mock(side_effect=True)

    # Case where there are no new stations in BC
    fake_check_new_station_in_bc.return_value = []

    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.debug.assert_any_call(f"Finished Unzipping MOE GW station list")
    fake_logger.info.assert_any_call("No new active stations in BC were found. Continuing on without inserting.")

    # Clean Up
    fake_logger.reset_mock()

    # Fails in the transform block
    fake_construct_insert_tables.side_effect = Exception("Error")
    fake_check_new_station_in_bc.return_value = ["testing"]

    with pytest.raises(RuntimeError, match=r"Failed to build LazyFrame to insert into the database for new stations.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.debug.assert_any_call(f"Finished Unzipping MOE GW station list")
    fake_logger.debug.assert_any_call("Constructing LazyFrames to insert in to the database")
    fake_logger.error.assert_called_once_with(Contains("Failed to build LazyFrame to insert into the database for new stations."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_construct_insert_tables.reset_mock(side_effect=True)

    # Fails inserting to table
    fake_construct_insert_tables.return_value = (pl.LazyFrame(), {})
    fake_insert_new_stations.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed inserting new stations and related metadata in to the database.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.debug.assert_any_call(f"Finished Unzipping MOE GW station list")
    fake_logger.debug.assert_any_call("Constructing LazyFrames to insert in to the database")
    fake_logger.error.assert_called_once_with(Contains("Failed inserting new stations and related metadata in to the database"), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_insert_new_stations.reset_mock(side_effect=True)
    fake_construct_insert_tables.reset_mock()
    fake_check_new_station_in_bc.reset_mock()

    # Success Case
    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with(f"Starting process of checking for new stations for {pipeline.name}")
    fake_logger.debug.assert_any_call(f"Getting Zipped folder from {MOE_GW_NEW_STATION_URL}")
    fake_logger.debug.assert_any_call(f"Finished Unzipping MOE GW station list")
    fake_logger.debug.assert_any_call("Constructing LazyFrames to insert in to the database")
    fake_logger.error.assert_not_called()
    fake_logger.warning.assert_not_called()

    fake_insert_new_stations.assert_called_once()
    fake_construct_insert_tables.assert_called_once()
    fake_check_new_station_in_bc.assert_called_once()

    assert fake_logger.debug.call_count == 3
    assert fake_logger.info.call_count == 1
