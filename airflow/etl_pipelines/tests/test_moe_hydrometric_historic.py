from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic import QuarterlyMoeHydroHistoricPipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_MOE_HYDRO_HIST_DESTINATION_TABLES,
    QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA,
    QUARTERLY_MOE_HYDRO_HIST_MIN_RATIO,
    QUARTERLY_MOE_HYDRO_HIST_NAME,
    QUARTERLY_MOE_HYDRO_HIST_RENAME_DICT,
    QUARTERLY_MOE_HYDRO_HIST_BASE_URL,
    QUARTERLY_MOE_HYDRO_HIST_NETWORK_ID
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

@patch.object(QuarterlyMoeHydroHistoricPipeline, "_QuarterlyMoeHydroHistoricPipeline__get_all_source_urls")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.logger")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.pl.read_database")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_initialization_discharge(
    fake_read_database,
    fake_logger,
    fake_get_all_urls
):
    # Set up fakes
    fake_read_database.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )


    # Initialize Pipeline
    pipeline = QuarterlyMoeHydroHistoricPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), archive_type="Discharge")

    # Assertion time
    assert pipeline.name == QUARTERLY_MOE_HYDRO_HIST_NAME
    assert pipeline.source_url == {}
    assert pipeline.destination_tables == QUARTERLY_MOE_HYDRO_HIST_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == ""
    assert pipeline.expected_dtype == QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == QUARTERLY_MOE_HYDRO_HIST_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == QUARTERLY_MOE_HYDRO_HIST_NETWORK_ID
    assert pipeline.min_ratio == QUARTERLY_MOE_HYDRO_HIST_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)
    assert pipeline.archive_type == "Discharge"
    assert pipeline.station_list == None

    plt.assert_frame_equal(
        pipeline.all_stations_in_network,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

    fake_logger.info.assert_called_once_with(f"Running Discharge Historical records update for {pipeline.name}")

@patch.object(QuarterlyMoeHydroHistoricPipeline, "_QuarterlyMoeHydroHistoricPipeline__get_all_source_urls")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.logger")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.pl.read_database")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_initialization_stage(
    fake_read_database,
    fake_logger,
    fake_get_all_urls
):
    # Set up fakes
    fake_read_database.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )


    # Initialize Pipeline
    pipeline = QuarterlyMoeHydroHistoricPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), archive_type="Stage")

    # Assertion time
    assert pipeline.name == QUARTERLY_MOE_HYDRO_HIST_NAME
    assert pipeline.source_url == {}
    assert pipeline.destination_tables == QUARTERLY_MOE_HYDRO_HIST_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == ""
    assert pipeline.expected_dtype == QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == QUARTERLY_MOE_HYDRO_HIST_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == QUARTERLY_MOE_HYDRO_HIST_NETWORK_ID
    assert pipeline.min_ratio == QUARTERLY_MOE_HYDRO_HIST_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)
    assert pipeline.archive_type == "Stage"
    assert pipeline.station_list == None

    plt.assert_frame_equal(
        pipeline.all_stations_in_network,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

    fake_logger.info.assert_called_once_with(f"Running Stage Historical records update for {pipeline.name}")

@patch.object(QuarterlyMoeHydroHistoricPipeline, "_QuarterlyMoeHydroHistoricPipeline__get_all_source_urls")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.logger")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.pl.read_database")
def test_transform_data_discharge(
    fake_read_database,
    fake_logger,
    fake_get_all_urls
):
    # Set up fakes
    fake_read_database.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = QuarterlyMoeHydroHistoricPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), archive_type="Discharge")

    # Restart mocks
    fake_logger.reset_mock()

    # Fails transformation block
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame()

    with pytest.raises(RuntimeError, match=r"Failed to materialize the LazyFrame with all the transformations applied."):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Starting Transformation for {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains("Failed to materialize the LazyFrame with all the transformations applied."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Success
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_discharge_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA["station_data"]
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting Transformation for {pipeline.name}")
    fake_logger.info.assert_any_call(f"Finished Transformation for {pipeline.name}")

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"Discharge"}
    assert pipeline._EtlPipeline__transformed_data["Discharge"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["Discharge"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["Discharge"]["df"],
        pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_discharge_output.csv",
            has_header=True,
            null_values=[""],
            schema_overrides={
                'station_id': pl.Int64,
                'datestamp': pl.Date,
                'value': pl.Float64,
                'qa_id': pl.Int8,
                'variable_id': pl.Int8,
                'symbol_id': pl.Int16
            }
        ),
        check_column_order=False,
        check_row_order=False
    )

@patch.object(QuarterlyMoeHydroHistoricPipeline, "_QuarterlyMoeHydroHistoricPipeline__get_all_source_urls")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.logger")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.pl.read_database")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_transform_data_stage(
    fake_read_database,
    fake_logger,
    fake_get_all_urls
):
    # Set up fakes
    fake_read_database.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = QuarterlyMoeHydroHistoricPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), archive_type="Stage")

    # Restart mocks
    fake_logger.reset_mock()

    # Fails transformation block
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame()

    with pytest.raises(RuntimeError, match=r"Failed to materialize the LazyFrame with all the transformations applied."):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Starting Transformation for {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains("Failed to materialize the LazyFrame with all the transformations applied."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Success
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_stage_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA["station_data"]
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Starting Transformation for {pipeline.name}")
    fake_logger.info.assert_any_call(f"Finished Transformation for {pipeline.name}")

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"Stage"}
    assert pipeline._EtlPipeline__transformed_data["Stage"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["Stage"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["Stage"]["df"],
        pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_stage_output.csv",
            has_header=True,
            null_values=[""],
            schema_overrides={
                'station_id': pl.Int64,
                'datestamp': pl.Date,
                'value': pl.Float64,
                'qa_id': pl.Int8,
                'variable_id': pl.Int8,
                'symbol_id': pl.Int16
            }
        ),
        check_column_order=False,
        check_row_order=False
    )

@patch.object(StationObservationPipeline, "insert_new_stations")
@patch.object(StationObservationPipeline, "construct_insert_tables")
@patch.object(StationObservationPipeline, "check_new_station_in_bc")
@patch.object(QuarterlyMoeHydroHistoricPipeline, "_QuarterlyMoeHydroHistoricPipeline__get_all_source_urls")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.logger")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.pl.read_database")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_and_insert_new_station(
    fake_read_database,
    fake_logger,
    fake_get_all_urls,
    fake_in_bc,
    fake_construct,
    fake_insert_stations
):
    # Set up fakes
    fake_read_database.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = QuarterlyMoeHydroHistoricPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), archive_type="Discharge")

    # Restart mocks
    fake_logger.reset_mock()

    # Case where no data was downloaded
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame()

    with pytest.raises(RuntimeError, match=r"Error when trying to check for new stations.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with("Getting new stations and inserting them into the database")
    fake_logger.error.assert_called_once_with(Contains("Error when trying to check for new stations. Please check the error and retry"), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # No new stations found
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_discharge_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA["station_data"]
    )

    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Getting new stations and inserting them into the database")
    fake_logger.info.assert_any_call("No new stations found, continuing on with transformation")

    # Clean Up
    fake_logger.reset_mock()

    # Case when it fails in check_new_station_in_bc
    pipeline._EtlPipeline__downloaded_data["station_data"] = (
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_discharge_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides=QUARTERLY_MOE_HYDRO_HIST_DTYPE_SCHEMA["station_data"]
        )
        .rename({"Location ID": "Location_ID"})
        .with_columns(Location_ID = pl.when(pl.col("Location_ID") == pl.lit("08NK0004")).then(pl.lit("new_station")).otherwise(pl.col("Location_ID")))
        .rename({"Location_ID": "Location ID"})
    )
    fake_in_bc.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Error when trying to check if new stations are in BC. Please check the error and retry.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Getting new stations and inserting them into the database")
    fake_logger.info.assert_any_call(Contains("new stations. Checking if they are in BC"))
    fake_logger.error.assert_called_once_with(Contains("Error when trying to check if new stations are in BC. Please check the error and retry."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_in_bc.reset_mock(side_effect=True)

    # Case when there is no new stations in BC
    fake_in_bc.return_value = []

    pipeline.get_and_insert_new_stations()


    fake_logger.info.assert_any_call("Getting new stations and inserting them into the database")
    fake_logger.info.assert_any_call(Contains("new stations. Checking if they are in BC"))
    fake_logger.info.assert_any_call("No new stations found in BC, continuing on with transformation")

    # Clean Up
    fake_logger.reset_mock()

    # Fails in construct_insert_tables
    fake_in_bc.return_value = ["new_station"]
    fake_construct.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Error when trying to construct insert tables. Please check the error and retry.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Getting new stations and inserting them into the database")
    fake_logger.info.assert_any_call(Contains("new stations. Checking if they are in BC"))
    fake_logger.error.assert_called_once_with(Contains("Error when trying to construct insert tables. Please check the error and retry."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_construct.reset_mock(side_effect=True)

    # Fails in insert_new_stations
    fake_construct.return_value = (pl.LazyFrame(), {})
    fake_insert_stations.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Error when trying to insert new stations. Please check the error and retry.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Getting new stations and inserting them into the database")
    fake_logger.info.assert_any_call(Contains("new stations. Checking if they are in BC"))
    fake_logger.error.assert_called_once_with(Contains("Error when trying to insert new stations. Please check the error and retry."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()
    fake_insert_stations.reset_mock(side_effect=True)

    # Success
    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_any_call("Getting new stations and inserting them into the database")
    fake_logger.info.assert_any_call(Contains("new stations. Checking if they are in BC"))
    fake_logger.info.assert_any_call("Finished getting new stations and inserting them into the database")

@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.requests.get")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.logger")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic.pl.read_database")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_get_all_source_urls(
    fake_read_database,
    fake_logger,
    fake_get,
):
    # This is an actual test that pings the internet. I know it's not isolated but I think it's the best way to test practical behaviour. Can be removed if not desired.
    # Set up fakes
    fake_read_database.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )
    with open("etl_pipelines/tests/test_constants/station_csv/moe_hydro_hist_url_page.txt", "r") as file:
        html_txt = file.read()

    fake_response = MagicMock()
    fake_text = PropertyMock(return_value=html_txt)
    fake_get.return_value = fake_response
    type(fake_response).text = fake_text

    pipeline = QuarterlyMoeHydroHistoricPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"), archive_type="Stage")

    assert pipeline.source_url == {'Stage.csv': 'https://www.env.gov.bc.ca/wsd/data_searches/water/Stage.csv', 'Stage_Archive_2015Oct_2017Oct.csv': 'https://www.env.gov.bc.ca/wsd/data_searches/water/Stage_Archive_2015Oct_2017Oct.csv', 'Stage_Archive_2017Oct_2019Oct.csv': 'https://www.env.gov.bc.ca/wsd/data_searches/water/Stage_Archive_2017Oct_2019Oct.csv', 'Stage_Archive_2019Oct_2021Oct.csv': 'https://www.env.gov.bc.ca/wsd/data_searches/water/Stage_Archive_2019Oct_2021Oct.csv', 'Stage_Archive_2021Oct_2023Oct.csv': 'https://www.env.gov.bc.ca/wsd/data_searches/water/Stage_Archive_2021Oct_2023Oct.csv', 'Stage_Archive_Post_20231001.csv': 'https://www.env.gov.bc.ca/wsd/data_searches/water/Stage_Archive_Post_20231001.csv', 'Stage_Archive_Pre_20151001.csv': 'https://www.env.gov.bc.ca/wsd/data_searches/water/Stage_Archive_Pre_20151001.csv'}
