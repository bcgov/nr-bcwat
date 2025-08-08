from etl_pipelines.tests.test_utils.StationObservationPipeline_object import TestStationObservationPipeline
from freezegun import freeze_time
from etl_pipelines.tests.test_constants.test_StationObservationPipeline_constants import (
    get_station_list_read_database,
    CHECK_FOR_NEW_STATIONS_DATA,
    NEW_STATION_CONSTRUCT_INSERT_DATA,
    NEW_STATION_CONSTRUCT_EXPECTED_OUTPUT,
    NEW_STATION_METADATA_EXPECTED_OUTPUT,
    MAKE_LAZY_FRAME_CASE_1,
    MAKE_LAZY_FRAME_CASE_2,
    LOAD_TABLE_INTO_DB_DATA
)
from mock import patch
from unittest.mock import MagicMock, PropertyMock
from psycopg2.extras import RealDictCursor
from io import BytesIO
import pytest
import pendulum
import polars as pl
import polars.testing as plt

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.pl.read_database")
@freeze_time("2025-07-29 00:00:00 PST")
def test_initialization(mock_read_database):
    # Initialize the SationObservationPipeline object to test
    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.Int64,
                "col2": pl.String,
                "col3": pl.Float32,
                "col4": pl.Boolean
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="test_connection",
        date_now=pendulum.now("UTC")
    )

    # Test the initialized attributes:
    assert etl.name == "test"
    assert etl.source_url == "test_url"
    assert etl.destination_tables == {"station_data": "test_table_1"}
    assert etl.expected_dtype == {
        "station_data": {
            "col1": pl.Int64,
            "col2": pl.String,
            "col3": pl.Float32,
            "col4": pl.Boolean
        }
    }
    assert etl.column_rename_dict == {
        "col1": "new_col1",
        "col2": "new_col2",
        "col3": "new_col3",
        "col4": "new_col4"
    }
    assert etl.go_through_all_stations == False
    assert etl.overrideable_dtype == True
    assert etl.network == ["0"]
    assert etl.min_ratio == 0
    assert etl.file_encoding == "utf8"
    assert etl.db_conn == "test_connection"
    assert etl.station_source == None
    assert etl.all_stations_in_network == None

    datetime_now = pendulum.now("UTC")

    assert etl.date_now == datetime_now
    plt.assert_frame_equal(
        pl.select(etl.end_date),
        pl.select(pl.datetime(
            year=datetime_now.year,
            month=datetime_now.month,
            day=datetime_now.day,
            hour=datetime_now.hour,
            second=datetime_now.second,
            time_zone=str(datetime_now.tz)
        ))
    )

    plt.assert_frame_equal(
        pl.select(etl.start_date),
        pl.select(pl.datetime(
            year=datetime_now.year,
            month=datetime_now.month,
            day=datetime_now.day-2,
            hour=datetime_now.hour,
            second=datetime_now.second,
            time_zone=str(datetime_now.tz)
        ))
    )

    # Test that the station_list get's properly populated
    mock_read_database.return_value = pl.DataFrame({"original_id": ["id1", "id2", "id3"], "station_id": [1, 2, 3]})
    etl = TestStationObservationPipeline(
        name="test",
        source_url={"station_source": "test_url"},
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source="test",
        expected_dtype={
            "station_data": {
                "col1": pl.Int64,
                "col2": pl.String,
                "col3": pl.Float32,
                "col4": pl.Boolean
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="test_connection",
        date_now=pendulum.now("UTC")
    )

    plt.assert_frame_equal(
        etl.station_list,
        pl.LazyFrame({"original_id": ["id1", "id2", "id3"], "station_id": [1, 2, 3]})
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.requests.get")
def test_download_data(mock_get):
    #Prepare the mock response
    get_response = MagicMock(name="response")
    status_code = PropertyMock(return_value=200)
    raw = PropertyMock(return_value=BytesIO(MAKE_LAZY_FRAME_CASE_1))

    mock_get.return_value = get_response
    type(get_response).status_code = status_code
    type(get_response).raw = raw


    # Initialize minimum required for the class to run method being tested
    etl = TestStationObservationPipeline(
        name="test",
        source_url={"station_source": "test_url"},
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.String,
                "col2": pl.Int64,
                "col3": pl.String,
                "col4": pl.Float32,
                "col5": pl.Float32
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4",
            "col5": "new_col5"
        },
        go_through_all_stations=True,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="connection",
        date_now=pendulum.now("UTC")
    )

    # Call the method being tested
    etl.download_data()

    # Assert the downloaded data
    assert list(etl._EtlPipeline__downloaded_data.keys()) == ["station_data"]
    plt.assert_frame_equal(
        etl._EtlPipeline__downloaded_data["station_data"],
        pl.LazyFrame(
            {
                "col1": [None,"value","4493"],
                "col2": [12,39,23],
                "col3": ["var1","var2","var3"],
                "col4": [-123.6441909494533,-121.898972387,-119.23871982],
                "col5": [55.29809818294311,53.2893198,66.23493890],
            },
            schema_overrides=etl.expected_dtype["station_data"]
        )
    )

    # Mock call Assertions
    mock_get.assert_called_once()
    status_code.assert_called_once()
    assert raw.call_count == 2
    assert get_response.raw.decode_content
    assert False


@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.execute_values")
def test_load_data_into_tables(mock_execute_values):
    # Create values to be mocked
    connection = MagicMock(name="db_conn")
    cursor = MagicMock(name="cursor")

    mock_execute_values.return_values = None
    connection.cursor.return_value = cursor

    # Initialize minimum required for the class to run method being tested
    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={},
        column_rename_dict={},
        go_through_all_stations=True,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn=connection,
        date_now=pendulum.now("UTC")
    )

    # Call the method being tested:
    etl._load_data_into_tables(insert_tablename = "test_table", data=LOAD_TABLE_INTO_DB_DATA, pkey = ["station_id", "variable_id", "datestamp"], truncate=False)

    # Assert that mocked methods and functions were called the correct amount
    mock_execute_values.assert_called_once()
    connection.cursor.assert_called_once()
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()

def test_make_polars_lazyframe():
    # Set the mock values here. Use PropertyMock to mock attributes of the class.
    response = MagicMock()
    raw = PropertyMock(return_value=MAKE_LAZY_FRAME_CASE_1)
    type(response).raw = raw

    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.String,
                "col2": pl.Int64,
                "col3": pl.String,
                "col4": pl.Float32,
                "col5": pl.Float32
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4",
            "col5": "new_col5"
        },
        go_through_all_stations=True,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="test_connection",
        date_now=pendulum.now("UTC")
    )

    # Call the function being tested
    data_output = etl._StationObservationPipeline__make_polars_lazyframe(response, "station_data")

    # Make sure that the lazyframes are expected
    plt.assert_frame_equal(
        data_output,
        pl.LazyFrame(
            {
                "col1":[None,"value","4493"],
                "col2":[12,39,23],
                "col3":["var1","var2","var3"],
                "col4":[-123.6441909494533,-121.898972387,-119.23871982],
                "col5":[55.29809818294311,53.2893198,66.23493890]
            },
            schema_overrides={
                "col1": pl.String,
                "col2": pl.Int64,
                "col3": pl.String,
                "col4": pl.Float32,
                "col5": pl.Float32
            }
        )
    )

    # Ensure that .raw was only accessed once
    raw.assert_called_once()

    # Change the return values and reset the mock
    raw = PropertyMock(return_value=MAKE_LAZY_FRAME_CASE_2)
    type(response).raw = raw

    # Change the attributes for the class being tested:
    etl.go_through_all_stations = False
    etl.overrideable_dtype = True
    etl.expected_dtype={
        "station_data": {
            "col1": pl.String,
            "col2": pl.Int64,
            "col3": pl.String,
        }
    }

    data_output = etl._StationObservationPipeline__make_polars_lazyframe(response, "station_data")

    # Make sure that the lazyframes are expected
    plt.assert_frame_equal(
        data_output,
        pl.LazyFrame(
            {
                "col1":["test","value","4493"],
                "col2":[12,39,23],
                "col3":["var1","var2","var3"],
            },
            schema_overrides={
                "col1": pl.String,
                "col2": pl.Int64,
                "col3": pl.String,
            }
        )
    )

    # Ensure that .raw was only accessed once
    raw.assert_called_once()


@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.pl.read_database")
@freeze_time("2025-07-29 00:00:00 PST")
def test_get_station_list(mock_read_database):
    # Initialize Class object with station_source set to None so that it doesn't automatically run the function being tested.
    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.Int64,
                "col2": pl.String,
                "col3": pl.Float32,
                "col4": pl.Boolean
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="test_connection",
        date_now=pendulum.now("UTC")
    )

    # Set mock value to be the fixture
    mock_read_database.side_effect = get_station_list_read_database
    etl.station_source = "test"

    etl.get_station_list()

    plt.assert_frame_equal(
        etl.station_list,
        pl.LazyFrame({
            "original_id": ["station1", "station2", "station3"],
            "station_id": [100, 200, 300]
        })
    )

    # Assert that the patched function got called the appropriate amount
    mock_read_database.assert_called_once()

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.pl.read_database")
@freeze_time("2025-07-29 00:00:00 PST")
def get_all_stations_in_network(mock_read_database):
    # Initialize Class object with station_source set to None so that it doesn't automatically run the function being tested.
    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.Int64,
                "col2": pl.String,
                "col3": pl.Float32,
                "col4": pl.Boolean
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="test_connection",
        date_now=pendulum.now("UTC")
    )

    mock_read_database.side_effect = get_station_list_read_database
    etl.station_source = "test"

    etl.get_all_stations_in_network()

    plt.assert_frame_equal(
        etl.station_list,
        pl.LazyFrame({
            "original_id": ["station1", "station2", "station3"],
            "station_id": [100, 200, 300]
        })
    )
    assert True

    # Assert that the patched function got called the appropriate amount
    mock_read_database.assert_called_once()

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.pl.read_database")
@freeze_time("2025-07-29 00:00:00 PST")
def test_check_for_new_stations(mock_read_database):
    # Initialize Class object with station_source set to None so that it doesn't automatically run the function being tested.
    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data1": {
                "col1": pl.String,
                "col2": pl.Float32,
                "col3": pl.String,
                "col4": pl.Float32,
                "col5": pl.Float32
            },
            "station_data2": {
                "col1": pl.String,
                "col2": pl.Float32,
                "col3": pl.String,
                "col4": pl.Float32,
                "col5": pl.Float32
            }
        },
        column_rename_dict={
            "col1": "original_id",
            "col2": "value",
            "col3": "variable",
            "col4": "longitude",
            "col5": "latitude"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="test_connection",
        date_now=pendulum.now("UTC")
    )
    etl.station_source = "test"

    etl._EtlPipeline__downloaded_data = CHECK_FOR_NEW_STATIONS_DATA

    mock_read_database.side_effect = get_station_list_read_database

    new_stations = etl.check_for_new_stations()

    # Check that the expected stations are returned by the function
    plt.assert_frame_equal(
        new_stations,
        pl.LazyFrame({
            "original_id": ["station5", "station4"]
        }),
        check_row_order=False
    )

    # Assert that the patched function got called the appropriate amount
    mock_read_database.assert_called_once()

@freeze_time("2025-07-29 00:00:00 PST")
def test_check_new_station_in_bc():
    connection = MagicMock(name="db_conn")
    cursor = MagicMock(name="cursor")

    connection.cursor.return_value = cursor
    cursor.fetchall.return_value = [('station5', True)]

    # Initialize Class object with station_source set to None so that it doesn't automatically run the function being tested.
    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data1": {
                "col1": pl.String,
                "col2": pl.Float32,
                "col3": pl.String,
                "col4": pl.Float32,
                "col5": pl.Float32
            },
            "station_data2": {
                "col1": pl.String,
                "col2": pl.Float32,
                "col3": pl.String,
                "col4": pl.Float32,
                "col5": pl.Float32
            }
        },
        column_rename_dict={
            "col1": "original_id",
            "col2": "value",
            "col3": "variable",
            "col4": "longitude",
            "col5": "latitude"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn=connection,
        date_now=pendulum.now("UTC")
    )
    etl.station_source = "test"

    # Format the data to be the correct shape before checking:
    station_data = (
        pl.concat([
            CHECK_FOR_NEW_STATIONS_DATA["station_data1"],
            CHECK_FOR_NEW_STATIONS_DATA["station_data2"]
        ])
        .rename(etl.column_rename_dict)
        .select(
            "original_id",
            "longitude",
            "latitude"
        )
        .filter(pl.col("original_id").is_in(["station5"]))
    )

    # Call the function
    in_bc_list = etl.check_new_station_in_bc(station_data)

    # Check that the expected stations are returned
    assert len(in_bc_list) == 1
    assert in_bc_list[0] == "station5"

    # Check that the connection and cursor were used the correct number of times
    connection.cursor.assert_called_once()
    cursor.fetchall.assert_called_once()
    cursor.execute.assert_called_once()

def test_construct_insert_tables():
    # Initialize Class object with minimum required for this function to run
    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.Int64,
                "col2": pl.String,
                "col3": pl.Float32,
                "col4": pl.Boolean
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn="test_connection",
        date_now=pendulum.now("UTC")
    )

    # call the function
    new_station_output, metadata_dict_output = etl.construct_insert_tables(NEW_STATION_CONSTRUCT_INSERT_DATA)

    plt.assert_frame_equal(
        new_station_output,
        NEW_STATION_CONSTRUCT_EXPECTED_OUTPUT,
        check_row_order=False,
        check_column_order=False,
        check_dtypes=True
    )

    for key in metadata_dict_output.keys():
        assert metadata_dict_output[key][0] == NEW_STATION_METADATA_EXPECTED_OUTPUT[key][0]
        plt.assert_frame_equal(
            metadata_dict_output[key][1],
            NEW_STATION_METADATA_EXPECTED_OUTPUT[key][1],
            check_row_order=False,
            check_column_order=False,
            check_dtypes=False
        )

    # check that the function returns the expected output

    assert True

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.pl.read_database")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.execute_values")
def test_insert_new_stations(mock_execute_values, mock_read_database):
    connection = MagicMock()
    mock_execute_values.return_value = None
    mock_read_database.return_value = pl.DataFrame({"original_id": ["station5"], "station_id":[404]})

    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.Int64,
                "col2": pl.String,
                "col3": pl.Float32,
                "col4": pl.Boolean
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn=connection,
        date_now=pendulum.now("UTC")
    )

    etl.insert_new_stations(NEW_STATION_CONSTRUCT_EXPECTED_OUTPUT, NEW_STATION_METADATA_EXPECTED_OUTPUT)

    # Assert that the number of times the cursor was made is the expected number of times.
    assert connection.cursor.call_count == 2
    assert connection.commit.call_count == 1

    assert mock_execute_values.call_count == 4
    assert mock_read_database.call_count == 3

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.execute_values")
def test_check_year_in_station_year(mock_execute_values):
    connection = MagicMock(name="db_conn")
    cursor = MagicMock(name="cursor")

    cursor.fetchall.return_value = {"station_id": [404]}
    connection.cursor.return_value = cursor
    mock_execute_values.return_value = None

    etl = TestStationObservationPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        days=2,
        station_source=None,
        expected_dtype={
            "station_data": {
                "col1": pl.Int64,
                "col2": pl.String,
                "col3": pl.Float32,
                "col4": pl.Boolean
            }
        },
        column_rename_dict={
            "col1": "new_col1",
            "col2": "new_col2",
            "col3": "new_col3",
            "col4": "new_col4"
        },
        go_through_all_stations=False,
        overrideable_dtype=True,
        network_ids=["0"],
        min_ratio=0,
        file_encoding="utf8",
        db_conn=connection,
        date_now=pendulum.now("UTC")
    )

    etl._EtlPipeline__transformed_data["station_data"] = {
        "df":pl.DataFrame({
            "station_id":[404,505,606],
            "variable_id": [1,2,2]
        })
    }

    etl.check_year_in_station_year()

    # Assert that the cursor was only created once, and that the execute and commits were only called once as well.
    connection.cursor.assert_called_once_with(cursor_factory=RealDictCursor)
    cursor.execute.assert_called_once()
    cursor.fetchall.assert_called_once()
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    mock_execute_values.assert_called_once()

    # Add more station_ids and reset the calls that have been made to the mock object
    cursor.fetchall.return_value = {"station_id": [404,505,606]}
    connection.reset_mock()
    cursor.reset_mock()
    mock_execute_values.reset_mock()

    etl.check_year_in_station_year()

    connection.cursor.assert_called_once_with(cursor_factory=RealDictCursor)
    cursor.execute.assert_called_once()
    cursor.fetchall.assert_called_once()
    cursor.close.assert_called_once()
    assert mock_execute_values.call_count == 0
    assert True
