from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import import HydatPipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_HYDAT_DESTINATION_TABLES,
    QUARTERLY_HYDAT_DTYPE_SCHEMA,
    QUARTERLY_HYDAT_MIN_RATIO,
    QUARTERLY_HYDAT_NAME,
    QUARTERLY_HYDAT_RENAME_DICT,
    QUARTERLY_HYDAT_STATION_SOURCE,
    QUARTERLY_HYDAT_BASE_URL,
    QUARTERLY_HYDAT_DISCHARGE_LEVEL_QUERIES,
    QUARTERLY_HYDAT_STATION_LIST_CSV_URL,
    QUARTERLY_HYDATE_NETWORK_ID
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch, MagicMock, PropertyMock
from callee import Contains
from io import StringIO
import polars as pl
import polars.testing as plt
import pendulum
import pytest

@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_initialization(
    fake_get_stations,
    fake_check_hydat
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == QUARTERLY_HYDAT_NAME
    assert pipeline.source_url == ""
    assert pipeline.destination_tables == QUARTERLY_HYDAT_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == QUARTERLY_HYDAT_STATION_SOURCE
    assert pipeline.expected_dtype == QUARTERLY_HYDAT_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == QUARTERLY_HYDAT_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert not pipeline.overrideable_dtype
    assert pipeline.network == QUARTERLY_HYDATE_NETWORK_ID
    assert pipeline.min_ratio == QUARTERLY_HYDAT_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)
    assert not pipeline.will_import
    assert pipeline.file_path == "data/"
    assert pipeline.sqlite_path == "data/Hydat.sqlite3"
    assert pipeline.station_csv_url == QUARTERLY_HYDAT_STATION_LIST_CSV_URL.format("20250905")

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.zipfile.ZipFile")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.open")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.sleep")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.requests.get")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_download_data(
    fake_logger,
    fake_get_stations,
    fake_get,
    no_sleep,
    fake_open,
    fake_zip,
    fake_check_hydat
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # requests.get fails
    fake_get.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=rf"Failed to download Hydat from {pipeline.source_url}.*"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Downloading Zipped Hydat from {pipeline.source_url}")
    fake_logger.warning.assert_any_call(f"Error downloading Hydat from URL: {pipeline.source_url}. Retrying...")
    fake_logger.error.assert_called_once_with(f"Failed to download Hydat from {pipeline.source_url}. Raising Error", exc_info=True)

    # Clean Up
    pipeline._EtlPipeline__download_num_retries = 0
    fake_get.reset_mock(side_effect = True)
    fake_logger.reset_mock()

    # Status code not 200
    fake_response = MagicMock()
    fake_get.return_value = fake_response
    type(fake_response).status_code = PropertyMock(return_value=1990)

    with pytest.raises(RuntimeError, match=rf"Response status was not 200 when trying to download Hydat. Raising Error"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Downloading Zipped Hydat from {pipeline.source_url}")
    fake_logger.warning.assert_any_call(f"Response status was not 200. Retrying...")
    fake_logger.error.assert_called_once_with(f"Response status was not 200 when trying to download Hydat. Raising Error", exc_info=True)

    # Clean UP
    fake_logger.reset_mock()
    type(fake_response).status_code = PropertyMock(return_value=200)

    # Open fails
    fake_open.side_effect = Exception("Error")

    with pytest.raises(IOError, match=r"Failed when trying to write the chunked zipped Hydat file to disk.*"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Downloading Zipped Hydat from {pipeline.source_url}")
    fake_logger.error.assert_called_once_with(Contains(f"Failed when trying to write the chunked zipped Hydat file to disk."), exc_info=True)

    # Clean UP
    fake_logger.reset_mock()
    fake_open.reset_mock(side_effect=True)
    fake_response.reset_mock()

    # Unzipping Zip fails
    fake_zip.side_effect = Exception("Error")
    fake_response.iter_conent.return_value = ["Something"]

    with pytest.raises(IOError, match=r"Failed when trying to unzip the Hydat file.*"):
        pipeline.download_data()

    fake_logger.info.assert_any_call(f"Downloading Zipped Hydat from {pipeline.source_url}")
    fake_logger.info.assert_any_call(f"Finished downloading Hydat, Unzipping the Zip file")
    fake_logger.error.assert_called_once_with(Contains(f"Failed when trying to unzip the Hydat file."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_zip.reset_mock(side_effect=True)
    fake_open.reset_mock()
    fake_zip.reset_mock()
    fake_get.reset_mock()
    fake_response.reset_mock()

    # Success
    pipeline.download_data()

    fake_logger.info.assert_any_call(f"Downloading Zipped Hydat from {pipeline.source_url}")
    fake_logger.info.assert_any_call(f"Finished downloading Hydat, Unzipping the Zip file")
    fake_logger.info.assert_any_call(f"Finished Unzipping Hydat")
    fake_open.assert_called_once()
    fake_zip.assert_called_once()
    fake_get.assert_called_once()
    fake_response.iter_content.assert_called_once()

@patch.object(HydatPipeline, "_HydatPipeline__read_sqlite_database")
@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_extract_data(
    fake_logger,
    fake_get_stations,
    fake_check_hydat,
    fake_sqlite
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Fails on the `station` table
    fake_sqlite.side_effect = lambda query: mock_extract(query, "STATIONS")

    with pytest.raises(IOError, match=r"Failed to extract data from STATIONS table from Hydat.sqlite3 database.*"):
        pipeline.extract_data()

    fake_logger.info.assert_called_once_with("Extracting data from the Hydat.sqlite3 database file")
    fake_logger.error.assert_called_once_with(Contains("Failed to extract data from STATIONS table from Hydat.sqlite3 database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Fails on the `operation_codes` table
    fake_sqlite.side_effect = lambda query: mock_extract(query, "OPERATION_CODES")

    with pytest.raises(IOError, match=r"Failed to extract data from OPERATION_CODES table from Hydat.sqlite3 database.*"):
        pipeline.extract_data()

    fake_logger.info.assert_any_call("Extracting data from the Hydat.sqlite3 database file")
    fake_logger.error.assert_called_once_with(Contains("Failed to extract data from OPERATION_CODES table from Hydat.sqlite3 database."), exc_info=True)

    assert fake_logger.info.call_count == 2

    # Clean Up
    fake_logger.reset_mock()

    # Fails on the `agency_list` table
    fake_sqlite.side_effect = lambda query: mock_extract(query, "AGENCY_LIST")

    with pytest.raises(IOError, match=r"Failed to extract data from AGENCY_LIST table from Hydat.sqlite3 database.*"):
        pipeline.extract_data()

    fake_logger.info.assert_any_call("Extracting data from the Hydat.sqlite3 database file")
    fake_logger.error.assert_called_once_with(Contains("Failed to extract data from AGENCY_LIST table from Hydat.sqlite3 database."), exc_info=True)

    assert fake_logger.info.call_count == 3

    # Clean Up
    fake_logger.reset_mock()

    # Fails on the `data_symbols` table
    fake_sqlite.side_effect = lambda query: mock_extract(query, "DATA_SYMBOLS")

    with pytest.raises(IOError, match=r"Failed to extract data from DATA_SYMBOLS table from Hydat.sqlite3 database.*"):
        pipeline.extract_data()

    fake_logger.info.assert_any_call("Extracting data from the Hydat.sqlite3 database file")
    fake_logger.error.assert_called_once_with(Contains("Failed to extract data from DATA_SYMBOLS table from Hydat.sqlite3 database."), exc_info=True)

    assert fake_logger.info.call_count == 4

    # Clean Up
    fake_logger.reset_mock()

    # Fails on the `stn_data_collection` table
    fake_sqlite.side_effect = lambda query: mock_extract(query, "STN_DATA_COLLECTION")

    with pytest.raises(IOError, match=r"Failed to extract data from STN_DATA_COLLECTION table from Hydat.sqlite3 database.*"):
        pipeline.extract_data()

    fake_logger.info.assert_any_call("Extracting data from the Hydat.sqlite3 database file")
    fake_logger.error.assert_called_once_with(Contains("Failed to extract data from STN_DATA_COLLECTION table from Hydat.sqlite3 database."), exc_info=True)

    assert fake_logger.info.call_count == 5

    # Clean Up
    fake_logger.reset_mock()

    # Fails on the `stn_regulation` table
    fake_sqlite.side_effect = lambda query: mock_extract(query, "STN_REGULATION")

    with pytest.raises(IOError, match=r"Failed to extract data from STN_REGULATION table from Hydat.sqlite3 database.*"):
        pipeline.extract_data()

    fake_logger.info.assert_any_call("Extracting data from the Hydat.sqlite3 database file")
    fake_logger.error.assert_called_once_with(Contains("Failed to extract data from STN_REGULATION table from Hydat.sqlite3 database."), exc_info=True)

    assert fake_logger.info.call_count == 6

    # Clean Up
    fake_logger.reset_mock()
    fake_sqlite.reset_mock()

    # Success
    fake_sqlite.side_effect = lambda query: mock_extract(query, "TABLE_THAT_WILL_NEVER_BE_IN_HYDAT")

    pipeline.extract_data()

    fake_sqlite.call_count = 6
    fake_logger.info.assert_any_call("Extracting data from the Hydat.sqlite3 database file")
    fake_logger.info.assert_any_call("Finished extracting the necessary data from Hydat.sqlite3.")
    fake_logger.error.assert_not_called()
    fake_logger.warning.assert_not_called()

    assert len(pipeline._EtlPipeline__downloaded_data.keys()) == 6
    assert set(pipeline._EtlPipeline__downloaded_data.keys()) == {"station", "operation_codes", "agency_list", "data_symbols", "stn_data_collection", "stn_regulation"}
    assert fake_logger.info.call_count == 8

@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_stations")
@patch.object(HydatPipeline, "_HydatPipeline__check_station_list_csv")
@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_get_and_insert_new_stations(
    fake_logger,
    fake_get_stations,
    fake_check_hydat,
    fake_check_station_list_csv,
    fake_check_for_new_stations
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # __check_for_new_stations fails
    fake_check_for_new_stations.side_effect = Exception("Error")

    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Checking for new stations that are in the Hydat.sqlite3 database")
    fake_logger.info.assert_any_call(f"Checking for new realtime stations from {pipeline.station_csv_url}")
    fake_logger.error.assert_called_once_with(Contains("Failed to check for new stations that are in the Hydat.sqlite3 database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_check_for_new_stations.reset_mock(side_effect=True)

    # __check_station_list_csv Fails
    fake_check_station_list_csv.side_effect = Exception("Error")
    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Checking for new stations that are in the Hydat.sqlite3 database")
    fake_logger.info.assert_any_call(f"Checking for new realtime stations from {pipeline.station_csv_url}")
    fake_logger.error.assert_called_once_with(Contains(f"Failed checking for new stations in the station list csv {pipeline.station_csv_url}."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_check_station_list_csv.reset_mock(side_effect=True)
    fake_check_for_new_stations.reset_mock()

    # Success
    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Checking for new stations that are in the Hydat.sqlite3 database")
    fake_logger.info.assert_any_call(f"Checking for new realtime stations from {pipeline.station_csv_url}")
    fake_logger.error.assert_not_called()
    fake_check_for_new_stations.assert_called_once()
    fake_check_station_list_csv.assert_called_once()


@patch.object(StationObservationPipeline, "load_data")
@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.sqlalchemy.create_engine")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_transform_data(
    fake_logger,
    fake_read_database,
    fake_create_engine,
    fake_check_hydat,
    fake_load_data
):
    # Set up fakes
    fake_read_database.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Fails reading reading database for Hydat Stations
    fake_read_database.reset_mock(return_value = True)

    fake_read_database.side_effect = lambda query, connection: mock_read_database(query, "bcwat_obs.station")

    with pytest.raises(RuntimeError, match=r"Failed to gather stations that are related to Hydat.*"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with("Transforming and loading historical data in 100 000 size chunks from Hydat")
    fake_logger.debug.assert_called_once_with("Getting all stations from database that is related to Hydat")
    fake_logger.error.assert_called_once_with(Contains("Failed to gather stations that are related to Hydat."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_read_database.side_effect = mock_read_database

    # Creating sqlalchemy engine that connects to sqlite3 fails
    fake_create_engine.side_effect = Exception("Error")

    with pytest.raises(IOError, match=r"Failed to connected to Hydat.sqlite3 database.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call("Transforming and loading historical data in 100 000 size chunks from Hydat")
    fake_logger.debug.assert_called_once_with("Getting all stations from database that is related to Hydat")
    fake_logger.info.assert_any_call("Connecting to Hydat.sqlite3 database using SQLalchemy")
    fake_logger.error.assert_called_once_with(Contains("Failed to connected to Hydat.sqlite3 database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_create_engine.reset_mock(side_effect=True)

    # Fails trying to load data
    fake_load_data.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to load data in to the database! Please check what happened and rerun."):
        pipeline.transform_data()

    fake_logger.info.assert_any_call("Transforming and loading historical data in 100 000 size chunks from Hydat")
    fake_logger.debug.assert_any_call("Getting all stations from database that is related to Hydat")
    fake_logger.info.assert_any_call("Connecting to Hydat.sqlite3 database using SQLalchemy")
    fake_logger.debug.assert_any_call("Transforming and Loading FLOW data in chunks.")
    fake_logger.error.assert_called_once_with(Contains("Failed to load data in to the database! Please check what happened and rerun."), exc_info=True)

    # Clean up
    fake_logger.reset_mock()
    fake_load_data.reset_mock(side_effect=True)
    fake_read_database.reset_mock()
    fake_create_engine.reset_mock()

    pipeline.transform_data()

    fake_logger.info.assert_any_call("Transforming and loading historical data in 100 000 size chunks from Hydat")
    fake_logger.debug.assert_any_call("Getting all stations from database that is related to Hydat")
    fake_logger.info.assert_any_call("Connecting to Hydat.sqlite3 database using SQLalchemy")
    fake_logger.debug.assert_any_call("Transforming and Loading FLOW data in chunks.")
    fake_logger.debug.assert_any_call(f"Finished loading 1277 rows of data into the database, likely more to come")
    fake_logger.debug.assert_any_call(f"Finished loading 1299 rows of data into the database, likely more to come")
    fake_logger.info.assert_any_call(f"Finished Transformation and Load step for {pipeline.name}")
    fake_logger.error.assert_not_called()
    fake_create_engine.assert_called_once_with("sqlite:///data/Hydat.sqlite3")

    assert fake_read_database.call_count == 3
    assert fake_load_data.call_count == 2

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"LEVEL"}

    assert pipeline._EtlPipeline__transformed_data["LEVEL"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["LEVEL"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["LEVEL"]["df"],
        pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_output.csv",
            has_header=True,
            schema_overrides={
                "station_id": pl.Int64,
                "variable_id": pl.Int32,
                "datestamp": pl.Date,
                "value": pl.Float64,
                "qa_id": pl.Int32,
                "symbol_id": pl.Int32
            }
        ),
        check_column_order=False,
        check_row_order=False
    )


@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.requests.head")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.requests.get")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_check_for_new_hydat(
    fake_logger,
    fake_get_stations,
    fake_get,
    fake_head
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    with patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat") as mock:
        mock = MagicMock()
        pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # requets.get fails
    fake_get.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to get a successful result from requests.get function when checking HYDAT date.*"):
        pipeline._HydatPipeline__check_for_new_hydat()

    fake_logger.error.assert_called_once_with(Contains("Failed to get a successful result from requests.get function when checking HYDAT date."), exc_info=True)

    # Clean Up
    fake_get.reset_mock(side_effect=True)
    fake_logger.reset_mock()

    # status_code is not 200
    fake_get_response = MagicMock()
    fake_get.return_value = fake_get_response
    type(fake_get_response).status_code = PropertyMock(return_value=2089)

    with pytest.raises(RuntimeError, match=r"Status code from the Hydat FTP page did not return 200. Raising Error.*"):
        pipeline._HydatPipeline__check_for_new_hydat()

    fake_logger.error.assert_called_once_with(Contains("Status code from the Hydat FTP page did not return 200. Raising Error."))

    # Clean up
    fake_logger.reset_mock()
    type(fake_get_response).status_code = PropertyMock(return_value=200)

    # requests.head fails
    type(fake_get_response).text = PropertyMock(return_value= open("etl_pipelines/tests/test_constants/station_csv/hydat_sqlite3_page.txt").read())
    fake_head.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"requests.head failed unexpectedly. Please check and rerun.*"):
        pipeline._HydatPipeline__check_for_new_hydat()

    fake_logger.error.assert_called_once_with(Contains("requests.head failed unexpectedly. Please check and rerun."), exc_info=True)

    # Clean Up
    fake_head.reset_mock(side_effect=True)
    fake_logger.reset_mock()

    # status_code is not 301
    fake_head_response = MagicMock()
    fake_head.return_value = fake_head_response
    type(fake_head_response).status_code = PropertyMock(return_value=2090)

    with pytest.raises(RuntimeError, match=r"Status code of requests.head is not 301! Raising Error.*"):
        pipeline._HydatPipeline__check_for_new_hydat()

    fake_logger.error.assert_called_once_with(Contains("Status code of requests.head is not 301! Raising Error"))

    # Clean up
    fake_logger.reset_mock()
    type(fake_head_response).status_code = PropertyMock(return_value=301)

    # Fails getting the data from the db
    type(fake_head_response).headers = PropertyMock(return_value={"Location": "https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/Hydat_sqlite3_20250715.zip"})

    pipeline.db_conn._MockDbConn__cursor.fetchall.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Error checking the Hydat Import date in the database.*"):
        pipeline._HydatPipeline__check_for_new_hydat()

    fake_logger.info.assert_called_once_with("Newest version of hydat available: 2025-07-15")
    fake_logger.error.assert_called_once_with(Contains("Error checking the Hydat Import date in the database."), exc_info=True)
    pipeline.db_conn.cursor().execute.assert_called_once_with(Contains("SELECT import_date FROM bcwat_lic.bc_data_import_date WHERE dataset='hydat';"))
    pipeline.db_conn.cursor().fetchall.assert_called_once()
    pipeline.db_conn.cursor().close.assert_called_once()

    # Clean up
    fake_logger.reset_mock()
    pipeline.db_conn.cursor().reset_mock(side_effect=True)

    # Success, but import date in db is > available Hydat date
    pipeline.db_conn._MockDbConn__cursor.fetchall.return_value = [(pendulum.date(year=2025, month=8, day=22),)]

    pipeline._HydatPipeline__check_for_new_hydat()

    fake_logger.info.assert_any_call("Newest version of hydat available: 2025-07-15")
    fake_logger.info.assert_any_call("Current Version of hydat in db: 2025-08-22")
    fake_logger.assert_not_called()
    pipeline.db_conn.cursor().execute.assert_called_once_with(Contains("SELECT import_date FROM bcwat_lic.bc_data_import_date WHERE dataset='hydat';"))
    pipeline.db_conn.cursor().fetchall.assert_called_once()
    pipeline.db_conn.cursor().close.assert_called_once()

    assert pipeline.source_url == "http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/Hydat_sqlite3_20250715.zip"
    assert not pipeline.will_import

    # Clean up
    fake_logger.reset_mock()
    pipeline.db_conn.cursor().reset_mock()

    # Success, and import date in db is < available Hydat Date
    pipeline.db_conn._MockDbConn__cursor.fetchall.return_value = [(pendulum.date(year=2025, month=4, day=20),)]

    pipeline._HydatPipeline__check_for_new_hydat()

    fake_logger.info.assert_any_call("Newest version of hydat available: 2025-07-15")
    fake_logger.info.assert_any_call("Current Version of hydat in db: 2025-04-20")
    fake_logger.assert_not_called()
    pipeline.db_conn.cursor().execute.assert_called_once_with(Contains("SELECT import_date FROM bcwat_lic.bc_data_import_date WHERE dataset='hydat';"))
    pipeline.db_conn.cursor().fetchall.assert_called_once()
    pipeline.db_conn.cursor().close.assert_called_once()

    assert pipeline.source_url == "http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/Hydat_sqlite3_20250715.zip"
    assert pipeline.will_import

@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database_uri")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_read_sqlite_database(
    fake_logger,
    fake_get_stations,
    fake_db_uri_read,
    fake_check_hydat,
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # No query is supplied
    with pytest.raises(ValueError, match=r"Empty query has been passed in! Please ensure that you are using this method properly!"):
        pipeline._HydatPipeline__read_sqlite_database()

    fake_logger.error.assert_called_once_with("Empty query has been passed in! Please ensure that you are using this method properly!")

    # Clean Up
    fake_logger.reset_mock()

    # Success
    pipeline._HydatPipeline__read_sqlite_database("query")

    fake_logger.debug.assert_not_called()
    fake_logger.info.assert_not_called()
    fake_logger.warning.assert_not_called()
    fake_logger.error.assert_not_called()
    fake_db_uri_read.assert_called_once()

@patch.object(StationObservationPipeline, "insert_new_stations")
@patch.object(StationObservationPipeline, "construct_insert_tables")
@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_check_for_new_stations(
    fake_logger,
    fake_get_stations,
    fake_check_hydat,
    fake_construct_insert_tables,
    fake_insert_new_stations
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # No new stations to add
    pipeline._EtlPipeline__downloaded_data["station"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_new_station.csv",
        infer_schema=False
    ).head(0)

    pipeline._HydatPipeline__check_for_new_stations()

    fake_logger.info.assert_called_once_with("There is no new stations in Hydat! Exiting out of function and moving on to inserting data.")

    # Clean Up
    fake_logger.reset_mock()

    # Construct Insert metadata table fails
    pipeline._EtlPipeline__downloaded_data = {
        "station": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_new_station.csv",
            infer_schema=False
        ).with_columns(STATION_NUMBER=pl.when(pl.col("STATION_NUMBER") == pl.lit("08GA010")).then(pl.lit("new_station_id")).otherwise(pl.col("STATION_NUMBER"))),
        "stn_data_collection": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_station_data_collection.csv",
            infer_schema=False
        ),
        "stn_regulation": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_station_regulation.csv",
            infer_schema=False
        ),
        "operation_codes": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_operation_code.csv",
            infer_schema=False
        ),
        "agency_list": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_agency_list.csv",
            infer_schema=False
        )
    }
    fake_construct_insert_tables.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to construct the metadata tables to be inserted in to the database.*"):
        pipeline._HydatPipeline__check_for_new_stations()

    fake_logger.info.assert_called_once_with("There are 1 new stations in Hydat! Inserting them into database.")
    fake_logger.error.assert_called_once_with(Contains("Failed to construct the metadata tables to be inserted in to the database. Please check and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_construct_insert_tables.reset_mock(side_effect=True)

    # insert_new_station fails
    fake_construct_insert_tables.return_value = (pl.LazyFrame(), {})
    fake_insert_new_stations.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to insert new stations in to the database. Please check and rerun.*"):
        pipeline._HydatPipeline__check_for_new_stations()

    fake_logger.info.assert_called_once_with("There are 1 new stations in Hydat! Inserting them into database.")
    fake_logger.error.assert_called_once_with(Contains("Failed to insert new stations in to the database. Please check and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_insert_new_stations.reset_mock(side_effect=True)
    fake_construct_insert_tables.reset_mock()

    # Success
    pipeline._HydatPipeline__check_for_new_stations()

    fake_logger.info.assert_called_once_with("There are 1 new stations in Hydat! Inserting them into database.")
    fake_construct_insert_tables.assert_called_once()
    fake_insert_new_stations.assert_called_once()

@patch.object(StationObservationPipeline, "construct_insert_tables")
@patch.object(StationObservationPipeline, "insert_new_stations")
@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.requests.get")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_check_station_list_csv(
    fake_logger,
    fake_get_stations,
    fake_get,
    fake_check_hydat,
    fake_insert_new_stations,
    fake_construct_insert_tables
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))
    # This function is assumed to be called before
    pipeline.get_all_stations_in_network()

    # requests.get fails
    fake_get.side_effect = Exception("Error")

    with pytest.raises(IOError, match=r"Failed to download station csv list from.*"):
        pipeline._HydatPipeline__check_station_list_csv()

    fake_logger.info.assert_called_once_with(f"Downloading station_list csv from {pipeline.station_csv_url}")
    fake_logger.error.assert_called_once_with(Contains("Failed to download station csv list from"), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_get.reset_mock(side_effect = True)

    # status_code not 200
    fake_response = MagicMock()
    fake_get.return_value = fake_response
    type(fake_response).status_code = PropertyMock(return_value=2081)

    with pytest.raises(IOError, match=r"Response status was not 200 when trying to download Hydat.*"):
        pipeline._HydatPipeline__check_station_list_csv()

    fake_logger.info.assert_called_once_with(f"Downloading station_list csv from {pipeline.station_csv_url}")
    fake_logger.error.assert_called_once_with("Response status was not 200 when trying to download Hydat. Raising Error")

    # Clean Up
    fake_logger.reset_mock()
    type(fake_response).status_code = PropertyMock(return_value=200)

    # pl.scan_csv fails
    type(fake_response).raw = PropertyMock(return_value=open("etl_pipelines/tests/test_constants/station_csv/hydat_new_csv_station.csv", "rb").read())

    with patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.scan_csv") as mock:
        mock.side_effect = Exception("error")

        with pytest.raises(RuntimeError, match=r"Failed to load downloaded station list csv to a polars LazyFrame.*"):
            pipeline._HydatPipeline__check_station_list_csv()

        fake_logger.info.assert_called_once_with(f"Downloading station_list csv from {pipeline.station_csv_url}")
        fake_logger.error.assert_called_once_with(Contains("Failed to load downloaded station list csv to a polars LazyFrame"), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # There are no new stations, fails trying to update stations existing in the db to realtime stations
    pipeline.db_conn.cursor().execute.side_effect = Exception("Error")

    with patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.scan_csv") as mock:
        mock.return_value = pl.LazyFrame({
            "ID": ["01AD009"],
            "Prov/Terr": ["BC"]
        })

        with pytest.raises(RuntimeError, match=r"Failed to update stations that should be turned back on for real time scraping.*"):
            pipeline._HydatPipeline__check_station_list_csv()

        fake_logger.info.assert_any_call(f"Downloading station_list csv from {pipeline.station_csv_url}")
        fake_logger.info.assert_any_call("No new stations found in the station list csv. Moving on")
        fake_logger.info.assert_any_call("Now updating stations that should be turned back on for real time scraping")
        fake_logger.error.assert_called_once_with(Contains("Failed to update stations that should be turned back on for real time scraping."), exc_info=True)

        pipeline.db_conn.cursor().execute.assert_called_once()

    # Clean Up
    fake_logger.reset_mock()
    pipeline.db_conn.cursor().reset_mock(side_effect = True)

    # New station exists, but fails in construct_insert_tables
    fake_construct_insert_tables.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to construct insertion dict for new stations from the station list csv.*"):
        pipeline._HydatPipeline__check_station_list_csv()

    fake_logger.info.assert_any_call(f"Downloading station_list csv from {pipeline.station_csv_url}")
    fake_logger.info.assert_any_call(Contains("new station(s) in the station list csv. Adding them in to the database"))
    fake_logger.error.assert_called_once_with(Contains("Failed to construct insertion dict for new stations from the station list csv."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_construct_insert_tables.reset_mock(side_effect=True)

    # insert_new_stations_fails
    fake_construct_insert_tables.return_value = (pl.LazyFrame(), {})
    fake_insert_new_stations.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to insert new stations from the station list csv.*"):
        pipeline._HydatPipeline__check_station_list_csv()

    fake_logger.info.assert_any_call(f"Downloading station_list csv from {pipeline.station_csv_url}")
    fake_logger.info.assert_any_call(Contains("new station(s) in the station list csv. Adding them in to the database"))
    fake_logger.error.assert_called_once_with(Contains("Failed to insert new stations from the station list csv."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_insert_new_stations.reset_mock(side_effect=True)
    fake_construct_insert_tables.reset_mock()
    fake_get.reset_mock()

    # Success Case
    pipeline._HydatPipeline__check_station_list_csv()

    fake_logger.info.assert_any_call(f"Downloading station_list csv from {pipeline.station_csv_url}")
    fake_logger.info.assert_any_call(Contains("new station(s) in the station list csv. Adding them in to the database"))
    fake_logger.info.assert_any_call("Finished inserting new stations from the station list csv")
    fake_logger.info.assert_any_call("Now updating stations that should be turned back on for real time scraping")
    fake_logger.info.assert_any_call("Finished updating stations that should be turned back on for real time scraping")
    fake_logger.error.assert_not_called()

    fake_get.assert_called_once()
    fake_construct_insert_tables.assert_called_once()
    fake_insert_new_stations.assert_called_once()

@patch.object(HydatPipeline, "_HydatPipeline__check_for_new_hydat")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import.logger")
@freeze_time("2025-09-05 00:00:00 UTC")
def test_update_hydat_import_date(
    fake_logger,
    fake_get_stations,
    fake_check_hydat,
):
    # Set up fakes
    fake_get_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = HydatPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Update fails
    pipeline.db_conn.cursor().execute.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Updating import date for Hydat failed!.*"):
        pipeline.update_hydat_import_date()

    fake_logger.error(Contains("Updating import date for Hydat failed!"), exc_info=True)

    pipeline.db_conn.cursor().execute.assert_called_once_with("""
                UPDATE
                    bcwat_lic.bc_data_import_date
                SET
                    import_date = CURRENT_DATE
                WHERE
                    dataset = 'hydat';
            """)
    pipeline.db_conn.cursor().close.assert_called_once()

    # Clean Up
    fake_logger.reset_mock()
    pipeline.db_conn.cursor().reset_mock(side_effect=True)

    # Success
    pipeline.update_hydat_import_date()

    fake_logger.info.assert_not_called()
    fake_logger.error.assert_not_called()

    pipeline.db_conn.cursor().execute.assert_called_once_with("""
                UPDATE
                    bcwat_lic.bc_data_import_date
                SET
                    import_date = CURRENT_DATE
                WHERE
                    dataset = 'hydat';
            """)
    pipeline.db_conn.cursor().close.assert_called_once()

def mock_extract(query, fail_value):
    if fail_value in query:
        raise Exception("Error")
    else:
        return

def mock_read_database(
    query,
    fail_trigger="string that will never be part of a query",
    connection=None,
    iter_batches=None,
    batch_size=None,
    infer_schema_length=None
):
    if fail_trigger in query:
        raise Exception("Error")

    if "SELECT station_id, original_id FROM bcwat_obs.station" in query:
        return pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    elif "SELECT DLY_FLOWS.STATION_NUMBER" in query:
        return [pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_flow_download.csv",
            has_header=True,
            infer_schema=True,
            infer_schema_length=None,
            null_values=[""]
        )]
    elif """SELECT DLY_LEVELS."STATION_NUMBER",""" in query:
        return [pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/hydat_level_download.csv",
            has_header=True,
            infer_schema=True,
            infer_schema_length=None,
            null_values=[""]
        )]
