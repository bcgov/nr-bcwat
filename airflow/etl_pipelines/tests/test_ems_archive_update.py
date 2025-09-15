from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update import QuarterlyEmsArchiveUpdatePipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_EMS_DESTINATION_TABLES,
    QUARTERLY_EMS_DTYPE_SCHEMA,
    QUARTERLY_EMS_MIN_RATIO,
    QUARTERLY_EMS_NAME,
    QUARTERLY_EMS_RENAME_DICT,
    QUARTERLY_EMS_CURRENT_URL,
    QUARTERLY_EMS_NETWORK_ID,
    QUARTERLY_EMS_COLS_TO_KEEP,
    QUARTERLY_EMS_DATABC_LAYER,
    QUARTERLY_EMS_HISTORICAL_URL,
    WATER_QUALITY_PARAMETER_DTYPE,
    WATER_QUALITY_UNIT_DTYPE,
    NEW_EMS_LOCATION_TYPE_CODE_MESSAGE,
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch, MagicMock, PropertyMock
from callee import Contains
from io import StringIO
import polars as pl
import polars_st as st
import polars.testing as plt
import pendulum
import pytest

@freeze_time("2025-09-04 00:00:00 UTC")
def test_initialization():
    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == QUARTERLY_EMS_NAME
    assert pipeline.source_url == QUARTERLY_EMS_CURRENT_URL
    assert pipeline.destination_tables == QUARTERLY_EMS_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == ''
    assert pipeline.expected_dtype == QUARTERLY_EMS_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == QUARTERLY_EMS_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert not pipeline.overrideable_dtype
    assert pipeline.network == QUARTERLY_EMS_NETWORK_ID
    assert pipeline.min_ratio == QUARTERLY_EMS_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)
    assert pipeline.station_list == None
    assert pipeline.file_path == "data/"
    assert pipeline.csv_path == "data/ems_sample_results_historic_expanded.csv"
    assert pipeline.databc_layer_name == QUARTERLY_EMS_DATABC_LAYER
    assert pipeline.historical_source == QUARTERLY_EMS_HISTORICAL_URL

@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.zipfile.ZipFile")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.open")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.sleep")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.requests.get")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_download_historical_data(
    fake_logger,
    fake_get,
    no_sleep,
    fake_open,
    fake_zip
):
    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where requests.get fails
    fake_get.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to download EMS data from.*"):
        pipeline.download_historical_data()

    fake_logger.info.assert_called_once_with(f"Downloading zipped EMS data from {pipeline.historical_source}")
    fake_logger.warning.assert_any_call(f"Error downloading EMS data from URL: {pipeline.historical_source}. Retrying...")
    fake_logger.error.assert_called_once_with(Contains(f"Failed to download EMS data from {pipeline.historical_source}."), exc_info=True)

    assert pipeline._EtlPipeline__download_num_retries == 3

    # Clean Up
    fake_get.reset_mock(side_effect = True)
    fake_logger.reset_mock()
    pipeline._EtlPipeline__download_num_retries = 0

    # Case when status_code not 200
    fake_response = MagicMock()
    fake_get.return_value = fake_response
    type(fake_response).status_code = PropertyMock(return_value=564)

    with pytest.raises(RuntimeError, match=r"Response status was not 200 when trying to download EMS data.*"):
        pipeline.download_historical_data()

    fake_logger.info.assert_called_once_with(f"Downloading zipped EMS data from {pipeline.historical_source}")
    fake_logger.warning.assert_any_call(f"Response status was not 200. Retrying...")
    fake_logger.error.assert_called_once_with("Response status was not 200 when trying to download EMS data. Raising Error", exc_info=True)

    assert pipeline._EtlPipeline__download_num_retries == 3

    # Clean Up
    fake_logger.reset_mock()
    pipeline._EtlPipeline__download_num_retries = 0

    # Fails Writing zipfile
    fake_open.side_effect = Exception("Error")
    type(fake_response).status_code = PropertyMock(return_value = 200)

    with pytest.raises(IOError, match=r"Failed when trying to write the chunked zipped EMS data file to disk.*"):
        pipeline.download_historical_data()

    fake_logger.info.assert_called_once_with(f"Downloading zipped EMS data from {pipeline.historical_source}")
    fake_logger.error.assert_called_once_with(Contains("Failed when trying to write the chunked zipped EMS data file to disk."), exc_info=True)

    # Clean UP
    fake_logger.reset_mock()
    fake_open.reset_mock(side_effect = True)

    # Case where Unzipping file fails
    fake_response.iter_content.return_value = ["Something"]
    fake_open.return_value = MagicMock()

    fake_zip.side_effect = Exception("Error")

    with pytest.raises(IOError, match=r"Failed when trying to unzip the EMS data file.*"):
        pipeline.download_historical_data()

    fake_logger.info.assert_any_call(f"Downloading zipped EMS data from {pipeline.historical_source}")
    fake_logger.info.assert_any_call(f"Finished downloading EMS data, Unzipping the Zip file")
    fake_logger.error.assert_called_once_with(Contains("Failed when trying to unzip the EMS data file."), exc_info=True)

    # Clean Up
    fake_zip.reset_mock(side_effect=True)
    fake_logger.reset_mock()

    # Success
    fake_unzip = MagicMock(name="unzip")
    fake_zip.return_value = fake_unzip

    pipeline.download_historical_data()

    fake_logger.info.assert_any_call(f"Downloading zipped EMS data from {pipeline.historical_source}")
    fake_logger.info.assert_any_call(f"Finished downloading EMS data, Unzipping the Zip file")
    fake_logger.info.assert_any_call(f"Finished Unzipping EMS data")



@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.bcdata.get_data")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.st.from_geopandas")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_download_station_data_from_databc(
    fake_logger,
    fake_st_gpd,
    fake_bcdata
):
    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # st.from_geopandas fails
    fake_st_gpd.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed trying to download data from DataBC using bcdata for EMS Stations."):
        pipeline.download_station_data_from_databc()

    fake_logger.info.assert_called_once_with("Using bcdata to download data from DataBC for EMS Stations")
    fake_logger.error.assert_called_once_with(Contains("Failed trying to download data from DataBC using bcdata for EMS Stations."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_st_gpd.reset_mock(side_effect = True)
    fake_bcdata.reset_mock()

    # Success
    fake_st_gpd.return_value = pl.DataFrame({"TEST":["things"]})

    pipeline.download_station_data_from_databc()

    fake_logger.info.assert_any_call("Using bcdata to download data from DataBC for EMS Stations")
    fake_logger.info.assert_any_call("Finished getting EMS station data from DataBC")

    fake_bcdata.assert_called_once()
    fake_st_gpd.assert_called_once()

    plt.assert_frame_equal(
        pipeline._EtlPipeline__downloaded_data["ems_stations"],
        pl.LazyFrame(
            {
                "test": ["things"]
            }
        ),
        check_row_order=False,
        check_column_order=False
    )

@patch.object(QuarterlyEmsArchiveUpdatePipeline, "load_data")
@patch.object(QuarterlyEmsArchiveUpdatePipeline, "_QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_params")
@patch.object(QuarterlyEmsArchiveUpdatePipeline, "_QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_units")
@patch.object(QuarterlyEmsArchiveUpdatePipeline, "get_and_insert_new_stations")
@patch.object(QuarterlyEmsArchiveUpdatePipeline, "_QuarterlyEmsArchiveUpdatePipeline__insert_metadata")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.pl.read_csv_batched")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.pl.LazyFrame.sink_csv")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_transform_data(
    fake_logger,
    fake_sink,
    fake_read_batched,
    fake_read_db,
    fake_insert_metadata,
    fake_get_and_insert_new_stations,
    fake_get_and_insert_new_units,
    fake_get_and_insert_new_params,
    fake_load_data
):
    # Some constant test values to keep code cleaner
    batch_reader_side_effect = [
        [
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_current_download.csv",
                has_header = True,
                infer_schema=True,
                infer_schema_length=None
            ),
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_historical_download.csv",
                has_header = True,
                infer_schema=True,
                infer_schema_length=None
            )
        ],
        None
    ]

    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # error getting the historical csv file
    with patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.pl.scan_csv") as mock:
        mock.side_effect = Exception("Error")

        with pytest.raises(RuntimeError, match=r"Failed to get downloaded data or opening CSV.*"):
            pipeline.transform_data()

        fake_logger.info.assert_called_once_with(f"Starting trasformation step for {pipeline.name}")
        fake_logger.error.assert_called_once_with(Contains("Failed to get downloaded data or opening CSV."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Sinking csv fails
    pipeline._EtlPipeline__downloaded_data = {
        "current": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_current_download.csv",
            has_header = True,
            infer_schema=True,
            infer_schema_length=None
        )
    }

    fake_sink.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to write to CSV.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.error.assert_called_once_with(Contains("Failed to write to CSV."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_sink.reset_mock(side_effect=True)

    # pl.read_csv_batched fails
    fake_read_batched.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to set up batch CSV reader.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.error.assert_called_once_with(Contains("Failed to set up batch CSV reader"), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_read_batched.reset_mock(side_effect=True)

    # Fails getting location_type_code from db
    fake_batch_reader = MagicMock(name="reader")
    fake_read_batched.return_value = fake_batch_reader
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect

    fake_read_db.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed when trying to get EMS location type codes from database.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.error.assert_called_once_with(Contains("Failed when trying to get EMS location type codes from database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_read_db.reset_mock(side_effect=True)
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect

    # Fails checking for new ems_stations
    fake_read_db.side_effect = read_db_side_effect

    with pytest.raises(RuntimeError, match=r"Failed checkinng for new location type codes.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.error.assert_called_once_with(Contains("Failed checkinng for new location type codes."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect

    # No new codes found
    fake_get_and_insert_new_stations.side_effect = Exception("Error")
    pipeline._EtlPipeline__downloaded_data["ems_stations"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_bcdata_station.csv",
        has_header=True,
        infer_schema=False
    ).with_columns(geometry=st.from_geojson("geometry").st.set_srid(3005)).rename(str.lower)

    with pytest.raises(RuntimeError, match=r"Failed to collect and insert new stations in to the database.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.error.assert_called_once_with(Contains("Failed to collect and insert new stations in to the database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect

    # New Codes Found
    pipeline._EtlPipeline__downloaded_data["ems_stations"] = pipeline._EtlPipeline__downloaded_data["ems_stations"].with_columns(location_type_cd = pl.when(pl.col("location_type_cd") == pl.lit("01")).then(pl.lit("9290")).otherwise(pl.col("location_type_cd")))


    with pytest.raises(RuntimeError, match=r"Failed to collect and insert new stations in to the database.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.warning.assert_called_once_with(NEW_EMS_LOCATION_TYPE_CODE_MESSAGE)
    fake_logger.error.assert_called_once_with(Contains("Failed to collect and insert new stations in to the database."), exc_info=True)
    fake_insert_metadata.assert_called_once()

    # Clean Up
    fake_logger.reset_mock()
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect
    pipeline._EtlPipeline__downloaded_data["ems_stations"] = pipeline._EtlPipeline__downloaded_data["ems_stations"].with_columns(location_type_cd = pl.when(pl.col("location_type_cd") == pl.lit("9290")).then(pl.lit("01")).otherwise(pl.col("location_type_cd")))
    fake_get_and_insert_new_stations.reset_mock(side_effect = True)

    # __get_and_insert_new_units fails
    fake_get_and_insert_new_units.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed trying to get and insert new units.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.info.assert_any_call("Getting and inserting new stations.")
    fake_logger.info.assert_any_call("Checking if there are new units")
    fake_logger.error.assert_called_once_with(Contains("Failed trying to get and insert new units."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect
    fake_get_and_insert_new_units.reset_mock(side_effect = True)

    # __get_and_insert_new_params fails
    fake_get_and_insert_new_units.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/water_quality_units.csv",
        schema_overrides={
            "unit_name": pl.String,
            "unit_id": pl.Int64
        }
    )
    fake_get_and_insert_new_params.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed trying to get and insert new parameters.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.info.assert_any_call("Getting and inserting new stations.")
    fake_logger.info.assert_any_call("Checking if there are new units")
    fake_logger.info.assert_any_call("Checking if there are new parameters in the data")
    fake_logger.error.assert_called_once_with(Contains("Failed trying to get and insert new parameters."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect
    fake_get_and_insert_new_params.reset_mock(side_effect = True)

    # Second round of transformations fails
    fake_get_and_insert_new_params.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/water_quality_params.csv",
        schema_overrides={
            "parameter_name": pl.String,
            "parameter_id": pl.Int64
        }
    )
    with pytest.raises(RuntimeError, match=r"Failed to transform second round of transformations, after the new stations insert.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.info.assert_any_call("Getting and inserting new stations.")
    fake_logger.info.assert_any_call("Checking if there are new units")
    fake_logger.info.assert_any_call("Checking if there are new parameters in the data")
    fake_logger.error.assert_called_once_with(Contains("Failed to transform second round of transformations, after the new stations insert."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect

    # load_data fails
    fake_get_and_insert_new_stations.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_stations_to_scrape.csv",
        has_header = True,
    ).with_columns(geometry=st.from_geojson("geometry").st.set_srid(3005))

    fake_load_data.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to load transformed data into the database.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.info.assert_any_call("Getting and inserting new stations.")
    fake_logger.info.assert_any_call("Checking if there are new units")
    fake_logger.info.assert_any_call("Checking if there are new parameters in the data")
    fake_logger.error.assert_called_once_with(Contains("Failed to load transformed data into the database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_batch_reader.next_batches.side_effect = batch_reader_side_effect
    fake_load_data.reset_mock(side_effect = True)

    # Success
    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting trasformation step for {pipeline.name}")
    fake_logger.info.assert_any_call("Concatenating the current and historical data, then writing to CSV since it's too big to load to memory")
    fake_logger.info.assert_any_call("Getting all EMS location type codes from database")
    fake_logger.info.assert_any_call("Checking if there are any new EMS location type codes that needs to be inserted into the database.")
    fake_logger.info.assert_any_call("No new location type codes found. Moving on")
    fake_logger.info.assert_any_call("Getting and inserting new stations.")
    fake_logger.info.assert_any_call("Checking if there are new units")
    fake_logger.info.assert_any_call("Checking if there are new parameters in the data")

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 2
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"df", "pkey"}
    assert pipeline._EtlPipeline__transformed_data["pkey"] == ["station_id", "datetimestamp", "parameter_id", "unit_id"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["df"],
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_output.csv",
            schema_overrides={
                'station_id': pl.Int64,
                'datetimestamp': pl.Datetime(time_unit='us', time_zone='America/Vancouver'),
                'parameter_id': pl.Int64,
                'unit_id': pl.Int64,
                'qa_id': pl.Int32,
                'location_purpose': pl.String,
                'sampling_agency': pl.String,
                'analyzing_agency': pl.String,
                'collection_method': pl.String,
                'sample_state': pl.String,
                'sample_descriptor': pl.String,
                'analytical_method': pl.String,
                'qa_index_code': pl.String,
                'value': pl.String,
                'value_text': pl.String,
                'value_letter': pl.String
            }
        ),
        check_column_order=False,
        check_row_order=False
    )

@patch.object(StationObservationPipeline, "insert_new_stations")
@patch.object(StationObservationPipeline, "construct_insert_tables")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_stations(
    fake_logger,
    fake_read_db,
    fake_construct,
    fake_insert_station
):
    fake_read_db.side_effect = read_db_side_effect
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))
    processed_data = pl.scan_csv("etl_pipelines/tests/test_constants/station_csv/ems_archive_update_processed_data.csv", infer_schema=False)

    # Fails getting the stations to scrape
    with pytest.raises(RuntimeError, match=r"Failed to check if there were new stations in the EMS Station data from DataBC.*"):
        pipeline.get_and_insert_new_stations(processed_data)

    fake_logger.info.assert_called_once_with("Checking if there are new stations in the EMS Station data from DataBC")
    fake_logger.error.assert_called_once_with(Contains('Failed to check if there were new stations in the EMS Station data from DataBC.'), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Collection fails
    pipeline._EtlPipeline__downloaded_data["ems_stations"] = pl.LazyFrame()

    with pytest.raises(RuntimeError, match=r"Failed to get the list of new stations in the data.*"):
        pipeline.get_and_insert_new_stations(processed_data)

    fake_logger.info.assert_called_once_with("Checking if there are new stations in the EMS Station data from DataBC")
    fake_logger.error.assert_called_once_with(Contains('Failed to get the list of new stations in the data.'), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # No new stations Found
    pipeline._EtlPipeline__downloaded_data["ems_stations"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_bcdata_station.csv",
        has_header=True,
        infer_schema=False
    ).with_columns(geometry=st.from_geojson("geometry").st.set_srid(3005)).rename(str.lower).head(0)

    pipeline.get_and_insert_new_stations(processed_data)

    fake_logger.info.assert_any_call("Checking if there are new stations in the EMS Station data from DataBC")
    fake_logger.info.assert_any_call("Found no new stations in the EMS Station data from DataBC")

    # Construct insert metadata tables fails
    pipeline._EtlPipeline__downloaded_data["ems_stations"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_bcdata_station.csv",
        has_header=True,
        infer_schema=False
    ).with_columns(
        geometry=st.from_geojson("geometry").st.set_srid(3005)
    ).rename(str.lower)
    fake_construct.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to construct the DataFrames to insert into the database.*"):
        pipeline.get_and_insert_new_stations(processed_data.with_columns(ems_id_depth=pl.when(pl.col("ems_id_depth") == pl.lit("0200509")).then(pl.lit("new_station")).otherwise(pl.col("ems_id_depth"))))

    fake_logger.info.assert_any_call("Checking if there are new stations in the EMS Station data from DataBC")
    fake_logger.info.assert_any_call("Constructing insert tables for new stations")
    fake_logger.error.assert_called_once_with(Contains('Failed to construct the DataFrames to insert into the database.'), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_construct.reset_mock(side_effect=True)

    # Insert new station fails
    fake_insert_station.side_effect = Exception("Error")
    fake_construct.return_value = (pl.LazyFrame(), {})

    with pytest.raises(RuntimeError, match=r"Failed to insert new stations in to the database.*"):
        pipeline.get_and_insert_new_stations(processed_data.with_columns(ems_id_depth=pl.when(pl.col("ems_id_depth") == pl.lit("0200509")).then(pl.lit("new_station")).otherwise(pl.col("ems_id_depth"))))

    fake_logger.info.assert_any_call("Checking if there are new stations in the EMS Station data from DataBC")
    fake_logger.info.assert_any_call("Constructing insert tables for new stations")
    fake_logger.info.assert_any_call(f"Inserting new stations for {pipeline.name} into the database")
    fake_logger.error.assert_called_once_with(Contains('Failed to insert new stations in to the database.'), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_insert_station.reset_mock(side_effect=True)

    # Success
    stations_to_scrape = pipeline.get_and_insert_new_stations(processed_data.with_columns(ems_id_depth=pl.when(pl.col("ems_id_depth") == pl.lit("0200509")).then(pl.lit("new_station")).otherwise(pl.col("ems_id_depth"))))

    fake_logger.info.assert_any_call("Checking if there are new stations in the EMS Station data from DataBC")
    fake_logger.info.assert_any_call("Constructing insert tables for new stations")
    fake_logger.info.assert_any_call(f"Inserting new stations for {pipeline.name} into the database")

    assert not stations_to_scrape.filter(pl.col("ems_id_depth")==pl.lit("new_station")).collect().is_empty()

@patch.object(QuarterlyEmsArchiveUpdatePipeline, "_QuarterlyEmsArchiveUpdatePipeline__insert_metadata")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_units(
    fake_logger,
    fake_read_db,
    fake_insert_meta
):
    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))
    processed_data = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_processed_data.csv",
        infer_schema=False,
        null_values=[""]
    )

    # Fails getting the units in db
    fake_read_db.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to get water quality units already in the database, please fix and rerun.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_units(processed_data)

    fake_logger.error.assert_called_once_with(Contains("Failed to get water quality units already in the database, please fix and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_read_db.reset_mock(side_effect=True)

    # Fails finding new units
    fake_read_db.side_effect = read_db_side_effect

    with pytest.raises(RuntimeError, match=r"Failed to find new units by comparing the units in the data against the units in the database.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_units(pl.LazyFrame())

    fake_logger.error.assert_called_once_with(Contains("Failed to find new units by comparing the units in the data against the units in the database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # No new units
    units = pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_units(processed_data)

    fake_logger.info.assert_called_once_with("There are no new units in the data. Moving on")

    plt.assert_frame_equal(
        units,
        read_db_side_effect("unit_name").lazy(),
        check_column_order=False,
        check_row_order=False
    )

    # Clean Up
    fake_logger.reset_mock()

    # New Unit Found but inserting metadata fails
    fake_insert_meta.side_effect = Exception("Error")
    with pytest.raises(RuntimeError, match=r"Failed to insert new units in to the database. Please fix and rerun.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_units(processed_data.with_columns(unit=pl.when(pl.col("ems_id") == pl.lit("E226128")).then(pl.lit("BlueWhales/Human")).otherwise(pl.col("unit"))))

    fake_logger.info.assert_called_once_with(Contains("Found new units in the data, inserting them into the database:"))
    fake_logger.error.assert_called_once_with(Contains("Failed to insert new units in to the database. Please fix and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_insert_meta.reset_mock(side_effect=True)

    # Success
    units = pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_units(processed_data.with_columns(unit=pl.when(pl.col("ems_id") == pl.lit("E226128")).then(pl.lit("BlueWhales/Human")).otherwise(pl.col("unit"))))

    fake_logger.info.assert_any_call(Contains("Found new units in the data, inserting them into the database:"))
    fake_logger.info.assert_any_call("Getting all units in database, including the new ones")

    plt.assert_frame_equal(
        units,
        read_db_side_effect("unit_name").lazy(),
        check_column_order=False,
        check_row_order=False
    )

@patch.object(QuarterlyEmsArchiveUpdatePipeline, "_QuarterlyEmsArchiveUpdatePipeline__insert_metadata")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.NLP")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.pl.read_database")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_params(
    fake_logger,
    fake_read_db,
    fake_nlp,
    fake_insert_meta
):
    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))
    processed_data = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_processed_data.csv",
        infer_schema=False,
        null_values=[""]
    )

    # Fails getting the parameters in db
    fake_read_db.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to get water quality parameters already in the database, please fix and rerun.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_params(processed_data)

    fake_logger.error.assert_called_once_with(Contains("Failed to get water quality parameters already in the database, please fix and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_read_db.reset_mock(side_effect=True)

    # Fails finding new parameters
    fake_read_db.side_effect = read_db_side_effect

    with pytest.raises(RuntimeError, match=r"Failed to find new parameters by comparing the parameters in the data against the parameters in the database.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_params(pl.LazyFrame())

    fake_logger.error.assert_called_once_with(Contains("Failed to find new parameters by comparing the parameters in the data against the parameters in the database."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # No new parameters
    parameters = pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_params(processed_data.limit(0))

    fake_logger.info.assert_called_once_with("There are no new parameters in the data. Moving on")

    plt.assert_frame_equal(
        parameters,
        read_db_side_effect("parameter_name").lazy(),
        check_column_order=False,
        check_row_order=False
    )

    # Clean Up
    fake_logger.reset_mock()

    # NLP Fails
    fake_nlp.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to run the Chemist NLP to group the parameters in to the correct grouping id. Please check and rerun.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_params(processed_data)

    fake_logger.info.assert_called_once_with("New parameters found. Spinning up NLP to determine the groupings.")
    fake_logger.error.assert_called_once_with(Contains("Failed to run the Chemist NLP to group the parameters in to the correct grouping id. Please check and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_nlp.reset_mock(side_effect=True)

    # NLP WORKS
    fake_chemist = MagicMock()
    fake_nlp.return_value = fake_chemist
    fake_chemist.predict.return_value = ("Too Much In Water",0.7)
    fake_insert_meta.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to insert new parameters in to the database.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_params(processed_data)

    fake_logger.info.assert_any_call("New parameters found. Spinning up NLP to determine the groupings.")
    fake_logger.info.assert_any_call(Contains("Found new parameters in the data, inserting them into the database:"))
    fake_logger.error.assert_called_once_with(Contains("Failed to insert new parameters in to the database."), exc_info=True)

    # Clean UP
    fake_logger.reset_mock()
    fake_insert_meta.reset_mock(side_effect=True)

    # Success
    params = pipeline._QuarterlyEmsArchiveUpdatePipeline__get_and_insert_new_params(processed_data)

    fake_logger.info.assert_any_call("New parameters found. Spinning up NLP to determine the groupings.")
    fake_logger.info.assert_any_call(Contains("Found new parameters in the data, inserting them into the database:"))
    fake_logger.info.assert_any_call("Getting all parameters in the database, including the ones that were just inserted.")

    plt.assert_frame_equal(
        params,
        read_db_side_effect("parameter_name").lazy(),
        check_column_order=False,
        check_row_order=False
    )

@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.execute_values")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_load_data(
    fake_logger,
    fake_execute,
):
    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Fails in the loading step
    pipeline._EtlPipeline__transformed_data["df"] = pl.DataFrame()

    with pytest.raises(RuntimeError, match=r"Failed to insert EMS data in to the database. Please fix and rerun.*"):
        pipeline.load_data()

    fake_logger.info.assert_called_once_with("Loading water quality data into the table bcat_obs.water_quality_hourly.")
    fake_logger.error.assert_called_once_with(Contains("Failed to insert EMS data in to the database. Please fix and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Success
    pipeline._EtlPipeline__transformed_data = {
        "df": pl.scan_csv("etl_pipelines/tests/test_constants/station_csv/ems_archive_update_output.csv"),
        "pkey": ["station_id", "datetimestamp", "parameter_id", "unit_id"]
    }

    pipeline.load_data()

    fake_logger.info.assert_any_call("Loading water quality data into the table bcat_obs.water_quality_hourly.")
    fake_logger.info.assert_any_call(Contains("Inserting a total of"))
    fake_logger.info.assert_any_call("Finished loading data for this batch. Collecting more batches to see if there are anymore data")
    fake_logger.error.assert_not_called()

@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.execute_values")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update.logger")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_insert_metadata(
    fake_logger,
    fake_execute,
):
    # Initialize Pipeline
    pipeline = QuarterlyEmsArchiveUpdatePipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # fail inserting
    fake_execute.side_effect = Exception("Error")
    with pytest.raises(RuntimeError, match=r"Failed to insert EMS test_table data in to the database. Please fix and rerun.*"):
        pipeline._QuarterlyEmsArchiveUpdatePipeline__insert_metadata(pl.DataFrame({"test_col1":[1,2,3], "test_col2":["a","b","c"], "test_col3":[4,5,6]}), "test_table", ["test_col1", "test_col2"])

    fake_logger.error.assert_called_once_with(Contains("Failed to insert EMS test_table data in to the database. Please fix and rerun."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_execute.reset_mock(side_effect=True)

    # Success
    pipeline._QuarterlyEmsArchiveUpdatePipeline__insert_metadata(data=pl.DataFrame({"test_col1":[1,2,3], "test_col2":["a","b","c"], "test_col3":[4,5,6]}), tablename="new_units", pkey=["test_col1", "test_col2"])

def read_db_side_effect(query, connection = None, schema_overrides = None):
    if "network_id" in query:
        return pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_station.csv",
            has_header = True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    elif "location_type_code" in query:
        return pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/ems_archive_update_location_code.csv",
            has_header = True,
            infer_schema=True,
            infer_schema_length=None
        )
    elif "unit_name" in query:
        return pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/water_quality_units.csv",
            has_header = True,
            schema_overrides={
                "unit_name": pl.String,
                "unit_id": pl.Int64
            }
        )
    elif "parameter_name" in query:
        return pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/water_quality_params.csv",
            has_header = True,
            schema_overrides={
                "parameter_name": pl.String,
                "parameter_id": pl.Int64
            }
        )
    elif "grouping_name" in query:
        return pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/water_quality_groupings.csv",
            has_header = True,
            schema_overrides={
                "grouping_name": pl.String,
                "grouping_id": pl.Int64
            }
        )
