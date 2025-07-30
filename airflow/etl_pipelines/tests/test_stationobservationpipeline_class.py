from etl_pipelines.tests.test_utils.StationObservationPipeline_object import TestStationObservationPipeline
from freezegun import freeze_time
from etl_pipelines.tests.test_constants.test_StationObservationPipeline_constants import (
    get_station_list_read_database,
    CHECK_FOR_NEW_STATIONS_DATA
)
from etl_pipelines.tests.conftest import(
    fake_db_conn
)
from mock import patch
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
        source_url="test_url",
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

def test_download_data():
    assert True

def test_load_data_into_tables():
    assert True

def test_make_polars_lazyframe():
    assert True

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

@freeze_time("2025-07-29 00:00:00 PST")
def test_check_new_station_in_bc():
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
        db_conn=fake_db_conn("test_connection"),
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
    )

    in_bc_list = etl.check_new_station_in_bc(station_data)
    assert True

def test_construct_insert_tables():
    assert True

def test_insert_new_stations():
    assert True

def test_check_year_in_station_year():
    assert True
