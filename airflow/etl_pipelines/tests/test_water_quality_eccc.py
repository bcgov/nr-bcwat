from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc import QuarterlyWaterQualityEcccPipeline
from etl_pipelines.utils.constants import(
    QUARTERLY_ECCC_DESTINATION_TABLES,
    QUARTERLY_ECCC_DTYPE_SCHEMA,
    QUARTERLY_ECCC_MIN_RATIO,
    QUARTERLY_ECCC_NAME,
    QUARTERLY_ECCC_RENAME_DICT,
    QUARTERLY_ECCC_STATION_SOURCE,
    QUARTERLY_ECCC_BASE_URLS,
    QUARTERLY_ECCC_STATION_NETWORK_ID
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


@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc.pl.read_database")
@freeze_time("2025-09-04 00:00:00 UTC")
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
    pipeline = QuarterlyWaterQualityEcccPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == QUARTERLY_ECCC_NAME
    assert pipeline.source_url == QUARTERLY_ECCC_BASE_URLS
    assert pipeline.destination_tables == QUARTERLY_ECCC_DESTINATION_TABLES
    assert pipeline.days == 2
    assert pipeline.station_source == QUARTERLY_ECCC_STATION_SOURCE
    assert pipeline.expected_dtype == QUARTERLY_ECCC_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == QUARTERLY_ECCC_RENAME_DICT
    assert not pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == QUARTERLY_ECCC_STATION_NETWORK_ID
    assert pipeline.min_ratio == QUARTERLY_ECCC_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)

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

    plt.assert_frame_equal(
        pipeline.all_stations_in_network,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/env_hydro_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc.urlopen")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc.sleep")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc.logger")
@patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc.pl.read_database")
@freeze_time("2025-09-04 00:00:00 UTC")
def test_download_data(
    fake_get_station_list,
    fake_logger,
    no_sleep,
    fake_urlopen
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
    pipeline = QuarterlyWaterQualityEcccPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # urlopen throws an exception
    fake_urlopen.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Failed to download data from URL:.*"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Downloading data for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(Contains("Downloading data from URL:"))
    fake_logger.warning.assert_any_call(Contains("Error downloading data from URL:"))
    fake_logger.error.assert_any_call(Contains("Error downloading data from URL:"), exc_info=True)
    fake_logger.error.assert_any_call(Contains("Failed to download data from URL:"))

    assert fake_logger.warning.call_count == 3
    assert fake_logger.error.call_count == 2
    assert fake_urlopen.call_count == 4

    # Clean Up
    fake_logger.reset_mock()
    fake_urlopen.reset_mock(side_effect=True)

    # Case where the status_code is not 200
    fake_response = MagicMock()
    fake_urlopen.return_value = fake_response
    type(fake_response).status = PropertyMock(return_value=256)

    with pytest.raises(RuntimeError, match=r"Failed to download data from URL:.*"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Downloading data for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(Contains("Downloading data from URL:"))
    fake_logger.warning.assert_any_call("Response status was not 200. Retrying...")
    fake_logger.error.assert_any_call("Response status was not 200. Raising Error and Exiting", exc_info=True)
    fake_logger.error.assert_any_call(Contains("Failed to download data from URL:"))

    assert fake_logger.warning.call_count == 3
    assert fake_logger.error.call_count == 2
    assert fake_urlopen.call_count == 4

    # Clean Up
    fake_logger.reset_mock()
    fake_urlopen.reset_mock()
    type(fake_response).status = PropertyMock(return_value = 200)

    # Case when scan_csv fails
    fake_response.read.side_effect = Exception("Error")

    with pytest.raises(RuntimeError, match=r"Error when loading data in to LazyFrame.*"):
        pipeline.download_data()

    fake_logger.info.assert_called_once_with(f"Downloading data for {pipeline.name}")
    fake_logger.debug.assert_any_call(Contains("Downloading data from URL:"))
    fake_logger.debug.assert_any_call("Loading data into LazyFrame")
    fake_logger.error.assert_called_once_with(Contains("Error when loading data in to LazyFrame,"))
    fake_logger.warning.assert_not_called()
    fake_urlopen.assert_called_once()
    fake_response.read.assert_called_once()

    assert fake_logger.debug.call_count == 2

    # Clean Up
    fake_logger.reset_mock()
    fake_urlopen.reset_mock()
    fake_response.reset_mock(side_effect=True)

    # Downloaded data is empty
    with patch("etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc.pl.scan_csv") as mock:
        mock.return_value = pl.LazyFrame()

        with pytest.raises(RuntimeError, match=r"Downloaded data is empty for URL:.*"):
            pipeline.download_data()

        fake_logger.info.assert_called_once_with(f"Downloading data for {pipeline.name}")
        fake_logger.debug.assert_any_call(Contains("Downloading data from URL:"))
        fake_logger.debug.assert_any_call("Loading data into LazyFrame")
        fake_logger.error.assert_called_once_with(Contains("Downloaded data is empty for URL:"))

        assert fake_logger.debug.call_count == 2

    # Clean up
    fake_logger.reset_mock()

    # Success
    csv_file = StringIO()
    fake_response.read.return_value = "etl_pipelines/tests/test_constants/station_csv/water_quality_eccc_download_raw.csv"

    pipeline.download_data()

    fake_logger.info.assert_any_call(f"Downloading data for {pipeline.name}")
    fake_logger.debug.assert_any_call(Contains("Downloading data from URL:"))
    fake_logger.debug.assert_any_call("Loading data into LazyFrame")
    fake_logger.info.assert_any_call(f"Finished downloading data for {pipeline.name}")

    assert fake_urlopen.call_count == 7
    assert fake_response.read.call_count == 7

    for key in pipeline._EtlPipeline__downloaded_data.keys():
        plt.assert_frame_equal(
            # Needed to do the .head(1) to trim down to one row because VSCODE keeps on adding a new line at the end, which pl.scan_csv
            # Takes as a new line for the csv values. Adding a row of nulls.
            pipeline._EtlPipeline__downloaded_data[key].head(1),
            pl.LazyFrame(
                {
                    "SITE_NO": ["\ntest_no"],
                    "DATE_TIME_HEURE": ["2025-09-04 12:12"],
                    "FLAG_MARQUEUR": ["F"],
                    "VALUE_VALEUR": ["1867.0701"],
                    "SDL_LDE": [1.12],
                    "MDL_LDM": ["test"],
                    "VMV_CODE": [1],
                    "UNIT_UNITÉ": ["m^3/cm"],
                    "VARIABLE": ["Earth"],
                    "VARIABLE_FR": ["Terre"],
                    "STATUS_STATUT": ["Dying"],
                    "SAMPLE_ID_ÉCHANTILLON": ["Today"]
                },
                schema_overrides=QUARTERLY_ECCC_DTYPE_SCHEMA[key]
            ),
            check_column_order=False,
            check_row_order=False
        )

def test_transform_data():
    assert True
