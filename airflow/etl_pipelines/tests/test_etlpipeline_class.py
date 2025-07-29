from etl_pipelines.tests.test_utils.EtlPipeline_object import TestEtlPipeline
from etl_pipelines.tests.test_constants.test_EltPipeline_constants import(
    validate_data_case_2,
    validate_data_case_3,
    validate_data_case_4,
    expected_dtype
)
from freezegun import freeze_time
from mock import patch
import polars as pl
import polars.testing as plt
import pytest

def test_initialization():

    # Initialize the Class object
    etl = TestEtlPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        expected_dtype={"test_col1": pl.Int64, "test_col2": pl.Int64},
        db_conn="test_connection"
    )

    # Assert that the initialization was successful
    assert etl.name == "test"
    assert etl.source_url == "test_url"
    assert etl.destination_tables == {"station_data": "test_table_1"}
    assert etl.expected_dtype == {"test_col1": pl.Int64, "test_col2": pl.Int64}
    assert etl.db_conn == "test_connection"

    # Tests private attributes
    assert etl._EtlPipeline__download_num_retries == 0
    assert etl._EtlPipeline__downloaded_data == {}
    assert etl._EtlPipeline__transformed_data == {}

@patch("etl_pipelines.scrapers.EtlPipeline.EtlPipeline._load_data_into_tables")
def test_load_data(mock_load_data_into_tables):
    # Assign mock values
    mock_load_data_into_tables.return_value = None

    # Initialize the Class object
    etl = TestEtlPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        expected_dtype={"test_col1": pl.Int64, "test_col2": pl.Int64},
        db_conn="test_connection"
    )

    # Assign transformed_data to be loaded.
    etl._EtlPipeline__transformed_data["station_data"] = {
        "df":pl.DataFrame({
            "id": [1,2,3,4,5],
            "col1" :["w", "a", "t", "e", "r"],
            "col2": [6,7,8,9,10]
        }),
        "pkey": ["id"],
        "truncate": False
    }

    # Call method being tested
    assert etl.load_data() == None

    # Check that the correct error gets raised when a key is missing:
    etl._EtlPipeline__transformed_data["station_data"] = {
        "data":pl.DataFrame({
            "id": [1,2,3,4,5],
            "col1" :["w", "a", "t", "e", "r"],
            "col2": [6,7,8,9,10]
        }),
        "pkey": ["id"],
        "truncate": False
    }

    with pytest.raises(KeyError):
        etl.load_data()

    etl._EtlPipeline__transformed_data["station_data"] = {
        "df":pl.DataFrame({
            "id": [1,2,3,4,5],
            "col1" :["w", "a", "t", "e", "r"],
            "col2": [6,7,8,9,10]
        }),
        "primary_key": ["id"],
        "truncate": False
    }

    with pytest.raises(RuntimeError):
        etl.load_data()

    etl._EtlPipeline__transformed_data["station_data"] = {
        "df":pl.DataFrame({
            "id": [1,2,3,4,5],
            "col1" :["w", "a", "t", "e", "r"],
            "col2": [6,7,8,9,10]
        }),
        "pkey": ["id"]
    }

    with pytest.raises(RuntimeError):
        etl.load_data()


def test_get_downloaded_data():
    # Initialize the Class object
    etl = TestEtlPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        expected_dtype={"test_col1": pl.Int64, "test_col2": pl.Int64},
        db_conn="test_connection"
    )

    # Assign a test downloaded data to the private attribute __downloaded_data.
    etl._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame({
        "id": [1,2,3,4,5],
        "col1" :["w", "a", "t", "e", "r"],
        "col2": [0,None,2,3,5]
    })

    # Call method being tested
    downloaded_data = etl.get_downloaded_data()

    # Assert that the downloaded data is correct
    assert list(downloaded_data.keys()) == ["station_data"]
    assert type(downloaded_data["station_data"]) is pl.LazyFrame

    plt.assert_frame_equal(
        downloaded_data["station_data"],
        pl.LazyFrame({
            "id": [1,2,3,4,5],
            "col1" :["w", "a", "t", "e", "r"],
            "col2": [0,None,2,3,5]
        })
    )

def test_get_transformed_data():
    # Initialize the Class object
    etl = TestEtlPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        expected_dtype={"test_col1": pl.Int64, "test_col2": pl.Int64},
        db_conn="test_connection"
    )

    # Assign a test transformed data to the private attribute __transformed_data_data.
    etl._EtlPipeline__transformed_data["station_data"] = {
        "df": pl.DataFrame({
            "id": [1,2,3,4,5],
            "col1" :["w", "a", "t", "e", "r"],
            "col2": [0,None,2,3,5]
        }).filter(pl.col("col2").is_not_null()),
        "pkey": ["id"],
        "truncate": False
    }

    # Call method being tested
    transformed_data = etl.get_transformed_data()

    # Assert that the transformed data is correct
    assert list(transformed_data.keys()) == ["station_data"]
    assert type(transformed_data["station_data"]) is dict
    assert type(transformed_data["station_data"]["df"]) is pl.DataFrame
    assert transformed_data["station_data"]["pkey"] == ["id"]
    assert transformed_data["station_data"]["truncate"] == False

    plt.assert_frame_equal(
        transformed_data["station_data"]["df"],
        pl.DataFrame({
            "id": [1,3,4,5],
            "col1" :["w","t","e","r"],
            "col2": [0,2,3,5]
        })
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.get_station_list")
def test_validate_downloaded_data(mock_get_station_list):
    # Initialize the Class object
    etl = TestEtlPipeline(
        name="test",
        source_url="test_url",
        destination_tables={"station_data": "test_table_1"},
        expected_dtype={"station_data": expected_dtype},
        db_conn="test_connection"
    )

    # Case 1: No data Downloaded
    etl._EtlPipeline__downloaded_data = {}

    with pytest.raises(ValueError):
        etl.validate_downloaded_data()

    # Case 2: Data Downloaded but wrong columns
    etl._EtlPipeline__downloaded_data["station_data"] = validate_data_case_2

    with pytest.raises(ValueError):
        etl.validate_downloaded_data()

    # Case 3: Data Downloaded but wrong types
    etl._EtlPipeline__downloaded_data["station_data"] = validate_data_case_3

    with pytest.raises(TypeError):
        etl.validate_downloaded_data()

    #Case 4: Data Downloaded and correct
    etl._EtlPipeline__downloaded_data["station_data"] = validate_data_case_4

    etl.validate_downloaded_data()
