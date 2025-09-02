from etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro import EnvHydroPipeline
from etl_pipelines.utils.constants import(
    ENV_HYDRO_DESTINATION_TABLES,
    ENV_HYDRO_DTYPE_SCHEMA,
    ENV_HYDRO_MIN_RATIO,
    ENV_HYDRO_NAME,
    ENV_HYDRO_NETWORK,
    ENV_HYDRO_RENAME_DICT,
    ENV_HYDRO_STATION_SOURCE,
    ENV_HYDRO_DISCHARGE_BASE_URL,
    ENV_HYDRO_STAGE_BASE_URL
)
from etl_pipelines.tests.conftest import (
    MockDbConn
)
from freezegun import freeze_time
from mock import patch
from callee import Contains
import polars as pl
import polars.testing as plt
import pendulum
import pytest

@patch("etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
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
    pipeline = EnvHydroPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == ENV_HYDRO_NAME
    assert pipeline.source_url == {"discharge": ENV_HYDRO_DISCHARGE_BASE_URL, "stage": ENV_HYDRO_STAGE_BASE_URL}
    assert pipeline.destination_tables == ENV_HYDRO_DESTINATION_TABLES
    assert pipeline.days == 3
    assert pipeline.station_source == ENV_HYDRO_STATION_SOURCE
    assert pipeline.expected_dtype == ENV_HYDRO_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == ENV_HYDRO_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == ENV_HYDRO_NETWORK
    assert pipeline.min_ratio == ENV_HYDRO_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=3)

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

@patch("etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro.EnvHydroPipeline.get_and_insert_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
def test_transform_data(
    fake_get_station_list,
    fake_logger,
    fake_get_and_insert_new_stations
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
    pipeline = EnvHydroPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # No downloaded data case
    with pytest.raises(RuntimeError, match="No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with("Starting Transformation Step")
    fake_logger.error.assert_called_once_with("No data downloaded. The attribute __downloaded_data is empty, will not transfrom data, exiting")

    # Clean Up
    fake_logger.reset_mock()

    # Case where it fails checking for stations
    pipeline._EtlPipeline__downloaded_data = {
        "discharge": pl.LazyFrame(schema=ENV_HYDRO_DTYPE_SCHEMA["discharge"]),
        "stage": pl.LazyFrame(schema=ENV_HYDRO_DTYPE_SCHEMA["stage"])
    }
    fake_get_and_insert_new_stations.side_effect = Exception("Error")

    pipeline.transform_data()

    fake_logger.info.assert_any_call("Starting Transformation Step")
    fake_logger.info.assert_any_call(f"Before transforming data, checking if there are new stations in the downloaded data")
    fake_logger.error.assert_called_once_with(Contains(f"There was an error when looking for/inserting new station metadata. Continuing without inserting new stations."))
    fake_logger.info.assert_any_call("Transformation complete for both Discharge and Stage")

    # Clean Up
    fake_logger.reset_mock()
    fake_get_and_insert_new_stations.reset_mock(side_effect=True)

    # Case where it fails in transformation
    pipeline._EtlPipeline__downloaded_data = {
        "discharge": pl.LazyFrame(),
        "stage": pl.LazyFrame(schema=ENV_HYDRO_DTYPE_SCHEMA["stage"])
    }

    with pytest.raises(RuntimeError, match=r"Error when trying to transform the downloaded data.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call("Starting Transformation Step")
    fake_logger.info.assert_any_call(f"Before transforming data, checking if there are new stations in the downloaded data")
    fake_logger.error.assert_called_once_with(Contains("Error when trying to transform the downloaded data."), exc_info=True)

    # Clean up
    fake_logger.reset_mock()

    # Success Case
    pipeline._EtlPipeline__downloaded_data = {
        "discharge": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/env_hydro_discharge_download.csv",
            schema_overrides=ENV_HYDRO_DTYPE_SCHEMA["discharge"],
            null_values=[""]
        ),
        "stage": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/env_hydro_stage_download.csv",
            schema_overrides=ENV_HYDRO_DTYPE_SCHEMA["stage"],
            null_values=[""]
        )
    }

    pipeline.transform_data()

    fake_logger.info.assert_any_call("Starting Transformation Step")
    fake_logger.info.assert_any_call(f"Before transforming data, checking if there are new stations in the downloaded data")
    fake_logger.info.assert_any_call("Transformation complete for both Discharge and Stage")
    fake_logger.error.assert_not_called()
    fake_logger.warning.assert_not_called()

    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"station_data"}
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        pl.read_csv(
            "etl_pipelines/tests/test_constants/station_csv/env_hydro_output.csv",
            null_values=[""],
            schema_overrides={
                'station_id': pl.Int64,
                'datestamp': pl.Date,
                'variable_id': pl.Int8,
                'value': pl.Float64,
                'qa_id': pl.Int8
            }
        ),
        check_column_order=False,
        check_row_order=False
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.insert_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.construct_insert_tables")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_new_station_in_bc")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_for_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro.pl.read_database")
@freeze_time("2025-09-02 00:00:00 UTC")
def test_get_and_insert_new_stations(
    fake_get_station_list,
    fake_logger,
    fake_check_for_new_stations,
    fake_check_new_stations_in_bc,
    fake_construct_tables,
    fake_insert_new_stations
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
    pipeline = EnvHydroPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))
    pipeline._EtlPipeline__downloaded_data = {
        "discharge": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/env_hydro_discharge_download.csv",
            schema_overrides=ENV_HYDRO_DTYPE_SCHEMA["discharge"],
            null_values=[""]
        ),
        "stage": pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/env_hydro_stage_download.csv",
            schema_overrides=ENV_HYDRO_DTYPE_SCHEMA["stage"],
            null_values=[""]
        )
    }

    # Case where check_for_new_stations fails
    fake_check_for_new_stations.side_effect = Exception("Check Error")

    with pytest.raises(RuntimeError, match=".*Check Error.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.error.assert_called_once_with("Error when trying to check for new stations.")
    fake_logger.info.assert_not_called()
    fake_logger.debug.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()
    fake_check_for_new_stations.reset_mock(side_effect=True)

    # Case where check_for_new_stations succeds but is empty
    fake_check_for_new_stations.return_value = pl.LazyFrame()

    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with("No new stations found, going back to transformation")
    fake_logger.error.assert_not_called()
    fake_logger.debug.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()

    # Case where check_new_stations_in_bc fails
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id": ["08NM0058", "08MH0056", "08HB0021"]})
    fake_check_new_stations_in_bc.side_effect = Exception("BC Error")

    with pytest.raises(RuntimeError, match=r".*BC Error.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.error.assert_called_once_with("Error when trying to check if new stations are in BC.")
    fake_logger.info.assert_not_called()
    fake_logger.debug.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()
    fake_check_new_stations_in_bc.reset_mock(side_effect=True)

    # Case where no new stations in BC were found
    fake_check_new_stations_in_bc.return_value = []

    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_called_once_with("No new stations found in BC, going back to transformation")
    fake_logger.error.assert_not_called()
    fake_logger.debug.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()

    # Case where there is a new station in BC but fails when construct_insert_tables is called
    fake_check_new_stations_in_bc.return_value = ["08NM0058"]
    fake_construct_tables.side_effect = Exception("Construction Falut")

    with pytest.raises(RuntimeError, match=r".*Construction Falut.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.error.assert_called_once_with("Error when trying to construct insert tables.")
    fake_logger.info.assert_not_called()
    fake_logger.debug.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()
    fake_construct_tables.reset_mock(side_effect=True)

    # Case where it fails inserting to DB
    fake_construct_tables.return_value = (pl.LazyFrame(), {})
    fake_insert_new_stations.side_effect = Exception("Insert Fail")

    with pytest.raises(RuntimeError, match=r".*Insert Fail.*"):
        pipeline.get_and_insert_new_stations()

    fake_logger.error.assert_called_once_with(Contains("Error when trying to insert new stations."))
    fake_logger.info.assert_not_called()
    fake_logger.debug.assert_not_called()

    # Clean Up
    fake_logger.reset_mock()
    fake_insert_new_stations.reset_mock(side_effect=True)
    fake_check_for_new_stations.reset_mock()
    fake_check_new_stations_in_bc.reset_mock()
    fake_construct_tables.reset_mock()
    fake_insert_new_stations.reset_mock()

    # Success Case
    pipeline.get_and_insert_new_stations()

    fake_logger.info.assert_not_called()
    fake_logger.debug.assert_not_called()
    fake_logger.error.assert_not_called()
    fake_logger.warning.assert_not_called()
    fake_check_for_new_stations.assert_called_once()
    fake_check_new_stations_in_bc.assert_called_once()
    fake_construct_tables.assert_called_once()
    fake_insert_new_stations.assert_called_once()
