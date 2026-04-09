from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.enmods_archive_update import QuarterlyEnmodsArchiveUpdatePipeline
from etl_pipelines.utils.constants import (
    ENMODS_DESTINATION_TABLES,
    ENMODS_DTYPE_SCHEMA,
    ENMODS_MIN_RATIO,
    ENMODS_RENAME_DICT,
    ENMODS_NETWORK_ID,
    QUARTERLY_ENMODS_NAME,
    QUARTERLY_ENMODS_COLS_TO_KEEP,
    QUARTERLY_ENMODS_URL_DICT,
    DAILY_ENMODS_NAME,
    DAILY_ENMODS_URL_DICT,
    NEW_ENMODS_LOCATION_TYPE_CODE_MESSAGE,
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch, call, MagicMock, PropertyMock
from callee import Contains
import polars as pl
import polars.testing as plt
import pendulum
import pytest
import os
from requests.exceptions import RequestException

MODULE_PATH = "etl_pipelines.scrapers.QuarterlyPipeline.quarterly.enmods_archive_update"

FIXTURE_DIR = "etl_pipelines/tests/test_constants/station_csv"


def read_db_side_effect(query, connection=None, schema_overrides=None):
    if "network_id" in query:
        return pl.read_csv(
            os.path.join(FIXTURE_DIR, "enmods_archive_update_station.csv"),
            has_header=True,
            schema_overrides={"original_id": pl.String, "station_id": pl.Int64},
        )
    elif "location_type_code" in query:
        return pl.read_csv(
            os.path.join(FIXTURE_DIR, "enmods_archive_update_location_code.csv"),
            has_header=True,
            infer_schema=True,
            infer_schema_length=None,
        )
    elif "unit_name" in query:
        return pl.read_csv(
            os.path.join(FIXTURE_DIR, "enmods_water_quality_units.csv"),
            has_header=True,
            schema_overrides={"unit_name": pl.String, "unit_id": pl.Int64},
        )
    elif "parameter_name" in query:
        return pl.read_csv(
            os.path.join(FIXTURE_DIR, "enmods_water_quality_params.csv"),
            has_header=True,
            schema_overrides={"parameter_name": pl.String, "parameter_id": pl.Int64},
        )
    elif "grouping_name" in query:
        return pl.read_csv(
            os.path.join(FIXTURE_DIR, "enmods_water_quality_groupings.csv"),
            has_header=True,
            schema_overrides={"grouping_name": pl.String, "grouping_id": pl.Int64},
        )

@freeze_time("2025-09-04 00:00:00 UTC")
@patch(f"{MODULE_PATH}.logger")
def test_initialization_quarterly(fake_logger):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC"), quarterly=True
    )

    assert pipeline.name == QUARTERLY_ENMODS_NAME
    assert pipeline.source_url == QUARTERLY_ENMODS_URL_DICT
    assert pipeline.destination_tables == ENMODS_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == ""
    assert pipeline.expected_dtype == ENMODS_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == ENMODS_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert not pipeline.overrideable_dtype
    assert pipeline.network == ENMODS_NETWORK_ID
    assert pipeline.min_ratio == ENMODS_MIN_RATIO
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pipeline.file_path == "data/"
    assert pipeline._tmp_files == []


@freeze_time("2025-09-04 00:00:00 UTC")
@patch(f"{MODULE_PATH}.logger")
def test_initialization_weekly(fake_logger):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC"), quarterly=False
    )

    assert pipeline.name == DAILY_ENMODS_NAME
    assert pipeline.source_url == DAILY_ENMODS_URL_DICT


def test_detect_compression_from_magic_bytes():
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_magic_bytes(
        b"PK\x03\x04extra"
    ) == "zip"
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_magic_bytes(
        b"\x1f\x8bextra"
    ) == "gz"
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_magic_bytes(
        b"7z\xbc\xaf\x27\x1c"
    ) == "7z"
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_magic_bytes(
        b"plaintext"
    ) is None
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_magic_bytes(
        b""
    ) is None


def test_detect_compression_from_headers():
    resp = MagicMock()

    # zip via Content-Disposition
    resp.headers = {"Content-Disposition": 'attachment; filename="data.zip"', "Content-Type": ""}
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_headers(resp) == "zip"

    # gz via Content-Type
    resp.headers = {"Content-Disposition": "", "Content-Type": "application/gzip"}
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_headers(resp) == "gz"

    # 7z via Content-Disposition
    resp.headers = {"Content-Disposition": 'filename="archive.7z"', "Content-Type": ""}
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_headers(resp) == "7z"

    # No compression signal
    resp.headers = {"Content-Disposition": "", "Content-Type": "text/csv"}
    assert QuarterlyEnmodsArchiveUpdatePipeline._detect_compression_from_headers(resp) is None

@patch(f"{MODULE_PATH}.os.rename")
@patch(f"{MODULE_PATH}.os.unlink")
@patch(f"{MODULE_PATH}.os.path.join", side_effect=lambda *a: "/".join(a))
@patch(f"{MODULE_PATH}.pl.scan_csv")
@patch(f"{MODULE_PATH}.requests.get")
@patch(f"{MODULE_PATH}.sleep")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_download_data_request_failure(
    fake_logger, no_sleep, fake_get, fake_scan, fake_join, fake_unlink, fake_rename
):
    """Test that download_data handles request failures with retries."""
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    # Simulate request exception on all retries
    fake_get.side_effect = RequestException("Connection failed")
    try:
        pipeline.download_data()
    except Exception as e:
        pytest.fail(f"download_data raised an exception instead of handling it: {e}")
    # All sources should have failed
    fake_logger.error.assert_called()
    fake_logger.warning.assert_called()


@patch(f"{MODULE_PATH}.os.rename")
@patch(f"{MODULE_PATH}.os.unlink")
@patch(f"{MODULE_PATH}.requests.get")
@patch(f"{MODULE_PATH}.sleep")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_download_data_non_200_status(
    fake_logger, no_sleep, fake_get, fake_unlink, fake_rename
):
    """Test that download_data handles non-200 status codes."""
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    fake_response = MagicMock()
    type(fake_response).status_code = PropertyMock(return_value=500)
    fake_get.return_value = fake_response

    pipeline.download_data()

    fake_logger.warning.assert_called()

@patch(f"{MODULE_PATH}.os.path.exists")
@patch(f"{MODULE_PATH}.os.unlink")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_clean_up(fake_logger, fake_unlink, fake_exists):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    pipeline._tmp_files = ["data/file1.parquet", "data/file2.parquet"]
    fake_exists.return_value = True

    # Parent clean_up may do other things; patch it to isolate
    with patch.object(StationObservationPipeline, "clean_up"):
        pipeline.clean_up()

    assert fake_unlink.call_count == 2
    assert pipeline._tmp_files == []
    fake_logger.debug.assert_any_call("Removed temp file: data/file1.parquet")
    fake_logger.debug.assert_any_call("Removed temp file: data/file2.parquet")


@patch(f"{MODULE_PATH}.os.path.exists")
@patch(f"{MODULE_PATH}.os.unlink")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_clean_up_handles_oserror(fake_logger, fake_unlink, fake_exists):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    pipeline._tmp_files = ["data/file1.parquet"]
    fake_exists.return_value = True
    fake_unlink.side_effect = OSError("Permission denied")

    with patch.object(StationObservationPipeline, "clean_up"):
        pipeline.clean_up()

    fake_logger.warning.assert_called_once_with(Contains("Failed to remove temp file"))
    assert pipeline._tmp_files == []

@patch.object(QuarterlyEnmodsArchiveUpdatePipeline, "load_data")
@patch.object(
    QuarterlyEnmodsArchiveUpdatePipeline,
    "_QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_params",
)
@patch.object(
    QuarterlyEnmodsArchiveUpdatePipeline,
    "_QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_units",
)
@patch.object(QuarterlyEnmodsArchiveUpdatePipeline, "get_and_insert_new_stations")
@patch.object(
    QuarterlyEnmodsArchiveUpdatePipeline,
    "_QuarterlyEnmodsArchiveUpdatePipeline__insert_metadata",
)
@patch(f"{MODULE_PATH}.pl.read_database")
@patch(f"{MODULE_PATH}.pq.ParquetFile")
@patch(f"{MODULE_PATH}.pl.LazyFrame.sink_parquet")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_transform_data(
    fake_logger,
    fake_sink,
    fake_parquet_file,
    fake_read_db,
    fake_insert_metadata,
    fake_get_and_insert_new_stations,
    fake_get_and_insert_new_units,
    fake_get_and_insert_new_params,
    fake_load_data,
):
    # Build arrow batches from the test fixture for the parquet batch reader
    test_batch_df = pl.read_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_observation_download.csv"),
        has_header=True,
        infer_schema=True,
        infer_schema_length=None,
    )
    arrow_batches = test_batch_df.to_arrow().to_batches()

    # Set up ParquetFile mock: each call to iter_batches returns a fresh iterator
    fake_pq_instance = MagicMock(name="parquet_reader")
    fake_parquet_file.return_value = fake_pq_instance
    fake_pq_instance.iter_batches.side_effect = lambda *a, **kw: iter(arrow_batches)

    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    with patch.object(pipeline, "get_downloaded_data", side_effect=Exception("Error")):
        with pytest.raises(RuntimeError, match=r"Failed to get downloaded data or opening CSV.*"):
            pipeline.transform_data()


    fake_logger.info.assert_called_once_with(Contains("Starting transformation step"))
    fake_logger.error.assert_called_once_with(
        Contains("Failed to get downloaded data or opening CSV."), exc_info=True
    )

    fake_logger.reset_mock()

    pipeline._EtlPipeline__downloaded_data = {
        "enmods_current": pl.scan_csv(
            os.path.join(FIXTURE_DIR, "enmods_archive_update_observation_download.csv"),
            has_header=True,
            infer_schema=True,
            infer_schema_length=None,
        ),
    }

    fake_sink.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to write combined parquet.*"):
        pipeline.transform_data()

    fake_logger.error.assert_called_once_with(
        Contains("Failed to write combined parquet."), exc_info=True
    )


    fake_logger.reset_mock()
    fake_sink.reset_mock(side_effect=True)

    fake_parquet_file.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to open combined parquet file for batched reading.*"):
        pipeline.transform_data()

    fake_logger.error.assert_called_once_with(
        Contains("Failed to open combined parquet file for batched reading"), exc_info=True
    )


    fake_logger.reset_mock()
    fake_parquet_file.reset_mock(side_effect=True)
    fake_parquet_file.return_value = fake_pq_instance

    # Fails getting location_type_code from db
    fake_read_db.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError,
        match=r"Failed when trying to get ENMODS location type codes from database.*",
    ):
        pipeline.transform_data()

    fake_logger.error.assert_called_once_with(
        Contains("Failed when trying to get ENMODS location type codes from database."),
        exc_info=True,
    )


    fake_logger.reset_mock()
    fake_read_db.reset_mock(side_effect=True)

    # Fails checking for new location type descriptions
    fake_read_db.side_effect = read_db_side_effect

    with pytest.raises(RuntimeError, match=r"Failed checking for new location type codes.*"):
        pipeline.transform_data()

    fake_logger.error.assert_called_once_with(
        Contains("Failed checking for new location type codes."), exc_info=True
    )


    fake_logger.reset_mock()

    # No new codes found, but get_and_insert_new_stations fails
    fake_get_and_insert_new_stations.side_effect = Exception("Error")

    # Add station data with TYPE column (new format)
    pipeline._EtlPipeline__downloaded_data["enmods_stations"] = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_station_data.csv"),
        has_header=True,
        infer_schema=False,
    )

    with pytest.raises(
        RuntimeError,
        match=r"Failed to collect and insert new stations in to the database.*",
    ):
        pipeline.transform_data()

    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.error.assert_called_once_with(
        Contains("Failed to collect and insert new stations in to the database."),
        exc_info=True,
    )


    fake_logger.reset_mock()

    # New location type description found
    # Replace one TYPE with something not in the DB
    pipeline._EtlPipeline__downloaded_data["enmods_stations"] = (
        pipeline._EtlPipeline__downloaded_data["enmods_stations"].with_columns(
            TYPE=pl.when(pl.col("TYPE") == pl.lit("Well"))
            .then(pl.lit("Alien Water Source"))
            .otherwise(pl.col("TYPE"))
        )
    )

    with pytest.raises(
        RuntimeError,
        match=r"Failed to collect and insert new stations in to the database.*",
    ):
        pipeline.transform_data()

    fake_logger.warning.assert_called_once_with(NEW_ENMODS_LOCATION_TYPE_CODE_MESSAGE)
    fake_insert_metadata.assert_called_once()

    # Verify the auto-generated code data was passed to insert_metadata
    inserted_data = fake_insert_metadata.call_args[1].get("data") or fake_insert_metadata.call_args[0][0]
    assert "location_type_code" in inserted_data.columns
    assert "location_type_description" in inserted_data.columns
    assert inserted_data["location_type_description"].to_list() == ["Alien Water Source"]


    fake_logger.reset_mock()
    fake_insert_metadata.reset_mock()
    pipeline._EtlPipeline__downloaded_data["enmods_stations"] = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_station_data.csv"),
        has_header=True,
        infer_schema=False,
    )
    fake_get_and_insert_new_stations.reset_mock(side_effect=True)

    # get_and_insert_new_units fails
    fake_get_and_insert_new_units.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed trying to get and insert new units.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call("Checking if there are new units")
    fake_logger.error.assert_called_once_with(
        Contains("Failed trying to get and insert new units."), exc_info=True
    )


    fake_logger.reset_mock()
    fake_get_and_insert_new_units.reset_mock(side_effect=True)

    # get_and_insert_new_params fails
    fake_get_and_insert_new_units.return_value = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "water_quality_units.csv"),
        schema_overrides={"unit_name": pl.String, "unit_id": pl.Int64},
    )
    fake_get_and_insert_new_params.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError, match=r"Failed trying to get and insert new parameters.*"
    ):
        pipeline.transform_data()

    fake_logger.info.assert_any_call("Checking if there are new parameters in the data")
    fake_logger.error.assert_called_once_with(
        Contains("Failed trying to get and insert new parameters."), exc_info=True
    )


    fake_logger.reset_mock()
    fake_get_and_insert_new_params.reset_mock(side_effect=True)

    # Second round of transformations fails
    fake_get_and_insert_new_params.return_value = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "water_quality_params.csv"),
        schema_overrides={"parameter_name": pl.String, "parameter_id": pl.Int64},
    )

    with pytest.raises(
        RuntimeError,
        match=r"Failed to transform second round of transformations, after the new stations insert.*",
    ):
        pipeline.transform_data()

    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to transform second round of transformations, after the new stations insert."
        ),
        exc_info=True,
    )

    fake_logger.reset_mock()

    fake_get_and_insert_new_stations.return_value = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_stations_to_scrape.csv"),
        has_header=True,
    )
    fake_load_data.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError, match=r"Failed to load transformed data into the database.*"
    ):
        pipeline.transform_data()

    fake_logger.error.assert_called_once_with(
        Contains("Failed to load transformed data into the database."), exc_info=True
    )

    fake_logger.reset_mock()
    fake_load_data.reset_mock(side_effect=True)

    pipeline.transform_data()

    fake_logger.info.assert_any_call(Contains("Starting transformation step"))
    fake_logger.info.assert_any_call(
        "Concatenating the current and historical data into a combined parquet file"
    )
    fake_logger.info.assert_any_call("Getting all ENMODS location type codes from database")
    fake_logger.info.assert_any_call(
        "Checking if there are any new ENMODS location type codes that needs to be inserted into the database."
    )
    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.info.assert_any_call("Getting and inserting new stations.")
    fake_logger.info.assert_any_call("Checking if there are new units")
    fake_logger.info.assert_any_call("Checking if there are new parameters in the data")

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 2
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"df", "pkey"}
    assert pipeline._EtlPipeline__transformed_data["pkey"] == [
        "station_id", "datetimestamp", "parameter_id", "unit_id"
    ]

@patch.object(StationObservationPipeline, "insert_new_stations")
@patch.object(StationObservationPipeline, "construct_insert_tables")
@patch(f"{MODULE_PATH}.pl.read_database")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_stations(
    fake_logger,
    fake_read_db,
    fake_construct,
    fake_insert_station,
):
    fake_read_db.side_effect = read_db_side_effect
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )
    processed_data = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_processed_data.csv"),
        infer_schema=False,
    )

    with pytest.raises(
        RuntimeError,
        match=r"Failed to check if there were new stations in the ENMODS Station data from DataBC.*",
    ):
        pipeline.get_and_insert_new_stations(processed_data)

    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to check if there were new stations in the ENMODS Station data from DataBC."
        ),
        exc_info=True,
    )


    fake_logger.reset_mock()

    pipeline._EtlPipeline__downloaded_data["enmods_stations"] = pl.LazyFrame()

    with pytest.raises(
        RuntimeError,
        match=r"Failed to get the list of new stations in the data.*",
    ):
        pipeline.get_and_insert_new_stations(processed_data)

    fake_logger.error.assert_called_once_with(
        Contains("Failed to get the list of new stations in the data."), exc_info=True
    )

    fake_logger.reset_mock()

    pipeline._EtlPipeline__downloaded_data["enmods_stations"] = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_station_data.csv"),
        has_header=True,
        infer_schema=False,
    ).head(0)

    pipeline.get_and_insert_new_stations(processed_data)

    fake_logger.info.assert_any_call(
        "Checking if there are new stations in the ENMODS Station data from DataBC"
    )
    # With empty station data, all stations go to anti-join but none match then no new stations
    # OR all have null coords and get filtered then logged accordingly


    fake_logger.reset_mock()

    # New station found but null lat/long gets filtered
    # E999999 in fixture has null coords, E290345 is a new station (not in DB)
    pipeline._EtlPipeline__downloaded_data["enmods_stations"] = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_station_data.csv"),
        has_header=True,
        infer_schema=False,
    )

    # Add E290345 as a new station by adding to processed_data
    test_processed = processed_data.with_columns(
        ems_id_depth=pl.when(pl.col("ems_id_depth") == pl.lit("E290345"))
        .then(pl.lit("E290345"))
        .otherwise(pl.col("ems_id_depth"))
    )

    fake_construct.return_value = (pl.LazyFrame(), {})

    stations = pipeline.get_and_insert_new_stations(test_processed)

    fake_logger.info.assert_any_call("Constructing insert tables for new stations")
    fake_logger.info.assert_any_call(
        Contains(f"Inserting new stations for {pipeline.name} into the database")
    )

    fake_logger.reset_mock()
    fake_construct.reset_mock()

    fake_construct.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError,
        match=r"Failed to construct the DataFrames to insert into the database.*",
    ):
        pipeline.get_and_insert_new_stations(test_processed)

    fake_logger.error.assert_called_once_with(
        Contains("Failed to construct the DataFrames to insert into the database."),
        exc_info=True,
    )


    fake_logger.reset_mock()
    fake_construct.reset_mock(side_effect=True)
    fake_construct.return_value = (pl.LazyFrame(), {})

    fake_insert_station.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError, match=r"Failed to insert new stations in to the database.*"
    ):
        pipeline.get_and_insert_new_stations(test_processed)

    fake_logger.info.assert_any_call(
        Contains(f"Inserting new stations for {pipeline.name} into the database")
    )
    fake_logger.error.assert_called_once_with(
        Contains("Failed to insert new stations in to the database."), exc_info=True
    )

    fake_logger.reset_mock()
    fake_insert_station.reset_mock(side_effect=True)

    stations_to_scrape = pipeline.get_and_insert_new_stations(test_processed)

    fake_logger.info.assert_any_call(
        "Checking if there are new stations in the ENMODS Station data from DataBC"
    )
    fake_logger.info.assert_any_call("Constructing insert tables for new stations")
    fake_logger.info.assert_any_call(
        Contains(f"Inserting new stations for {pipeline.name} into the database")
    )

    # Verify the result is a LazyFrame with the expected columns
    result = stations_to_scrape.collect()
    assert "ems_id_depth" in result.columns


@patch.object(StationObservationPipeline, "insert_new_stations")
@patch.object(StationObservationPipeline, "construct_insert_tables")
@patch(f"{MODULE_PATH}.pl.read_database")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_stations_filters_null_coords(
    fake_logger, fake_read_db, fake_construct, fake_insert_station
):
    """Verify that stations with null latitude/longitude are filtered out before insert."""
    fake_read_db.side_effect = read_db_side_effect
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    # Station data where the only "new" station has null coords
    pipeline._EtlPipeline__downloaded_data["enmods_stations"] = pl.LazyFrame({
        "ID": ["E999999"],
        "NAME": ["NULL COORD STATION"],
        "TYPE": ["Well"],
        "LATITUDE": [None],
        "LONGITUDE": [None],
    }).cast({"LATITUDE": pl.Float64, "LONGITUDE": pl.Float64})

    processed_data = pl.LazyFrame({
        "ems_id": ["E999999"],
        "ems_id_depth": ["E999999"],
        "collection_start": ["2024-01-01T00:00:00-08:00"],
        "parameter": ["pH"],
        "result": ["7.0"],
        "unit": ["pH units"],
        "location_purpose": ["None of the above"],
        "sample_descriptor": ["General"],
        "qa_index_code": ["T"],
        "result_letter": [""],
        "result_text": ["7.0"],
        "sampling_agency": ["MOE"],
        "analyzing_agency": ["MOE LAB"],
        "collection_method": ["Grab"],
        "sample_state": ["Fresh Water"],
        "analytical_method": ["X100"],
        "parameter_code_units": [None],
    })

    result = pipeline.get_and_insert_new_stations(processed_data)

    # construct_insert_tables should NOT have been called since null coords filtered all new stations
    fake_construct.assert_not_called()
    fake_insert_station.assert_not_called()

@patch.object(
    QuarterlyEnmodsArchiveUpdatePipeline,
    "_QuarterlyEnmodsArchiveUpdatePipeline__insert_metadata",
)
@patch(f"{MODULE_PATH}.pl.read_database")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_units(fake_logger, fake_read_db, fake_insert_meta):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )
    processed_data = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_processed_data.csv"),
        infer_schema=False,
        null_values=[""],
    )

    fake_read_db.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError,
        match=r"Failed to get water quality units already in the database, please fix and rerun.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_units(
            processed_data
        )

    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to get water quality units already in the database, please fix and rerun."
        ),
        exc_info=True,
    )


    fake_logger.reset_mock()
    fake_read_db.reset_mock(side_effect=True)

    fake_read_db.side_effect = read_db_side_effect

    with pytest.raises(
        RuntimeError,
        match=r"Failed to find new units by comparing the units in the data against the units in the database.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_units(
            pl.LazyFrame()
        )

    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to find new units by comparing the units in the data against the units in the database."
        ),
        exc_info=True,
    )

    fake_logger.reset_mock()

    units = pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_units(
        processed_data
    )

    fake_logger.info.assert_any_call("There are no new units in the data. Moving on")

    plt.assert_frame_equal(
        units,
        read_db_side_effect("unit_name").lazy(),
        check_column_order=False,
        check_row_order=False,
    )

    fake_logger.reset_mock()

    fake_insert_meta.side_effect = Exception("Error")
    with pytest.raises(
        RuntimeError,
        match=r"Failed to insert new units in to the database. Please fix and rerun.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_units(
            processed_data.with_columns(
                unit=pl.when(pl.col("ems_id") == pl.lit("E226128"))
                .then(pl.lit("BlueWhales/Human"))
                .otherwise(pl.col("unit"))
            )
        )

    fake_logger.info.assert_any_call(
        Contains("Found new units in the data, inserting them into the database:")
    )
    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to insert new units in to the database. Please fix and rerun."
        ),
        exc_info=True,
    )


    fake_logger.reset_mock()
    fake_insert_meta.reset_mock(side_effect=True)

    # Success
    units = pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_units(
        processed_data.with_columns(
            unit=pl.when(pl.col("ems_id") == pl.lit("E226128"))
            .then(pl.lit("BlueWhales/Human"))
            .otherwise(pl.col("unit"))
        )
    )

    fake_logger.info.assert_any_call(
        Contains("Found new units in the data, inserting them into the database:")
    )
    fake_logger.info.assert_any_call(
        "Getting all units in database, including the new ones"
    )

    plt.assert_frame_equal(
        units,
        read_db_side_effect("unit_name").lazy(),
        check_column_order=False,
        check_row_order=False,
    )

@patch.object(
    QuarterlyEnmodsArchiveUpdatePipeline,
    "_QuarterlyEnmodsArchiveUpdatePipeline__insert_metadata",
)
@patch(f"{MODULE_PATH}.NLP")
@patch(f"{MODULE_PATH}.pl.read_database")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_params(
    fake_logger, fake_read_db, fake_nlp, fake_insert_meta
):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )
    processed_data = pl.scan_csv(
        os.path.join(FIXTURE_DIR, "enmods_archive_update_processed_data.csv"),
        infer_schema=False,
        null_values=[""],
    )

    #Fails getting parameters from db
    fake_read_db.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError,
        match=r"Failed to get water quality parameters already in the database, please fix and rerun.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_params(
            processed_data
        )

    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to get water quality parameters already in the database, please fix and rerun."
        ),
        exc_info=True,
    )


    fake_logger.reset_mock()
    fake_read_db.reset_mock(side_effect=True)

    # Fails finding new params
    fake_read_db.side_effect = read_db_side_effect

    with pytest.raises(
        RuntimeError,
        match=r"Failed to find new parameters by comparing the parameters in the data against the parameters in the database.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_params(
            pl.LazyFrame()
        )

    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to find new parameters by comparing the parameters in the data against the parameters in the database."
        ),
        exc_info=True,
    )


    fake_logger.reset_mock()

    # No new parameters
    parameters = (
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_params(
            processed_data.limit(0)
        )
    )

    fake_logger.info.assert_any_call(
        "There are no new parameters in the data. Moving on"
    )

    plt.assert_frame_equal(
        parameters,
        read_db_side_effect("parameter_name").lazy(),
        check_column_order=False,
        check_row_order=False,
    )

    fake_logger.reset_mock()

    fake_nlp.side_effect = RuntimeError("Error")
    # insert a new parameter to trigger the NLP grouping, but NLP fails
    processed_data = processed_data.with_columns(
            parameter=pl.when(pl.col("ems_id") == pl.lit("E226128"))
            .then(pl.lit("Unobtainium Dissolved"))
            .otherwise(pl.col("parameter"))
        )
    with pytest.raises(
        RuntimeError,
        match=r"Failed to run the Chemist NLP to group the parameters in to the correct grouping id.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_params(
            processed_data
        )

    fake_logger.info.assert_any_call(
        "New parameters found. Spinning up NLP to determine the groupings."
    )
    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to run the Chemist NLP to group the parameters in to the correct grouping id."
        ),
        exc_info=True,
    )

    fake_logger.reset_mock()
    fake_nlp.reset_mock(side_effect=True)

    #NLP works, insert fails
    fake_chemist = MagicMock()
    fake_nlp.return_value = fake_chemist
    fake_chemist.predict.return_value = ("Too Much In Water", 0.7)
    fake_insert_meta.side_effect = Exception("Error")

    with pytest.raises(
        RuntimeError,
        match=r"Failed to insert new parameters in to the database.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_params(
            processed_data
        )

    fake_logger.info.assert_any_call(
        "New parameters found. Spinning up NLP to determine the groupings."
    )
    fake_logger.info.assert_any_call(
        Contains("Found new parameters in the data, inserting them into the database:")
    )
    fake_logger.error.assert_called_once_with(
        Contains("Failed to insert new parameters in to the database."), exc_info=True
    )


    fake_logger.reset_mock()
    fake_insert_meta.reset_mock(side_effect=True)

    # Success
    params = (
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__get_and_insert_new_params(
            processed_data
        )
    )

    fake_logger.info.assert_any_call(
        "New parameters found. Spinning up NLP to determine the groupings."
    )
    fake_logger.info.assert_any_call(
        Contains("Found new parameters in the data, inserting them into the database:")
    )
    fake_logger.info.assert_any_call(
        "Getting all parameters in the database, including the ones that were just inserted."
    )

    plt.assert_frame_equal(
        params,
        read_db_side_effect("parameter_name").lazy(),
        check_column_order=False,
        check_row_order=False,
    )

@patch(f"{MODULE_PATH}.execute_values")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_load_data(fake_logger, fake_execute):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    # Fails in loading step
    pipeline._EtlPipeline__transformed_data["df"] = pl.DataFrame()

    with pytest.raises(
        RuntimeError,
        match=r"Failed to insert ENMODS data in to the database. Please fix and rerun.*",
    ):
        pipeline.load_data()

    fake_logger.info.assert_called_once_with(
        "Loading water quality data into the table bcat_obs.water_quality_hourly."
    )
    fake_logger.error.assert_called_once_with(
        Contains("Failed to insert ENMODS data in to the database. Please fix and rerun."),
        exc_info=True,
    )


    fake_logger.reset_mock()

    # Success
    output_path = os.path.join(FIXTURE_DIR, "enmods_archive_update_output.csv")
    if os.path.exists(output_path):
        pipeline._EtlPipeline__transformed_data = {
            "df": pl.scan_csv(output_path),
            "pkey": ["station_id", "datetimestamp", "parameter_id", "unit_id"],
        }
    else:
        # Minimal data if fixture doesn't exist yet
        pipeline._EtlPipeline__transformed_data = {
            "df": pl.LazyFrame({
                "station_id": [1],
                "datetimestamp": ["2024-01-01"],
                "parameter_id": [1],
                "unit_id": [1],
                "qa_id": [1],
                "location_purpose": ["test"],
                "sampling_agency": ["test"],
                "analyzing_agency": ["test"],
                "collection_method": ["test"],
                "sample_state": ["test"],
                "sample_descriptor": ["test"],
                "analytical_method": ["test"],
                "qa_index_code": ["T"],
                "value": ["1.0"],
                "value_text": ["1.0"],
                "value_letter": [""],
            }),
            "pkey": ["station_id", "datetimestamp", "parameter_id", "unit_id"],
        }

    pipeline.load_data()

    fake_logger.info.assert_any_call(
        "Loading water quality data into the table bcat_obs.water_quality_hourly."
    )
    fake_logger.info.assert_any_call(Contains("Inserting a total of"))
    fake_logger.info.assert_any_call(
        "Finished loading data for this batch. Collecting more batches to see if there are anymore data"
    )
    fake_logger.error.assert_not_called()

@patch(f"{MODULE_PATH}.execute_values")
@patch(f"{MODULE_PATH}.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_insert_metadata(fake_logger, fake_execute):
    pipeline = QuarterlyEnmodsArchiveUpdatePipeline(
        db_conn=MockDbConn(), date_now=pendulum.now("UTC")
    )

    test_data = pl.DataFrame({
        "test_col1": [1, 2, 3],
        "test_col2": ["a", "b", "c"],
        "test_col3": [4, 5, 6],
    })

    # Fail inserting
    fake_execute.side_effect = Exception("Error")
    with pytest.raises(
        RuntimeError,
        match=r"Failed to insert ENMODS test_table data in to the database. Please fix and rerun.*",
    ):
        pipeline._QuarterlyEnmodsArchiveUpdatePipeline__insert_metadata(
            test_data, "test_table", ["test_col1", "test_col2"]
        )

    fake_logger.error.assert_called_once_with(
        Contains(
            "Failed to insert ENMODS test_table data in to the database. Please fix and rerun."
        ),
        exc_info=True,
    )


    fake_logger.reset_mock()
    fake_execute.reset_mock(side_effect=True)

    # Success
    pipeline._QuarterlyEnmodsArchiveUpdatePipeline__insert_metadata(
        data=test_data, tablename="new_units", pkey=["test_col1", "test_col2"]
    )

    fake_execute.assert_called_once()
