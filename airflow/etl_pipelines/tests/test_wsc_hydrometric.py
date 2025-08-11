from freezegun import freeze_time
from mock import patch
from etl_pipelines.utils.constants import (
    WSC_URL,
    WSC_DESTINATION_TABLES,
    WSC_NAME
)
from etl_pipelines.tests.test_constants.test_wsc_hydrometric_constants import(
    transform_case_2,
    transform_case_3,
    transform_case_4,
    transform_case_5,
    transform_case_station_id,
)
import polars as pl
import pytz
import pytest
import numpy as np
import pendulum

@freeze_time("2025-04-16 00:00:00 PST")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.get_station_list")
def test_initialization(mock_get_station_list):
    # This mock happens to ensure that the database is not accessed while testing.
    # The function get_station_list is not unique to this pipeline, so it is mocked.
    mock_get_station_list.return_value = None

    # Importing the class has to happen after the patch, or else the get_station_list will be called before it gets patched.
    from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline
    pipeline = WscHydrometricPipeline(db_conn="FakeDBConnection", date_now=pendulum.now("UTC"))

    # Assert initialization attributes for WscHydrometricPipeline class
    assert pipeline.days == 2
    assert pipeline.station_list == None

    assert pipeline.source_url == {"wsc_daily_hydrometric.csv": WSC_URL.format("20250416")}

    assert pipeline.end_date == pendulum.now("America/Vancouver")
    assert pipeline.start_date == pendulum.now("America/Vancouver").subtract(days=2)

    # Assert Initialization Attributes for parent class StationObservationPipeline
    assert not pipeline.go_through_all_stations

    # Assert Initialization attributes for parent class EtlPipeline
    assert pipeline.name == WSC_NAME
    assert pipeline.destination_tables == WSC_DESTINATION_TABLES
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.get_station_list")
@freeze_time("2025-04-16 08:00:00", tz_offset=-8)
def test_transform_data(mock_get_station_list):
    mock_get_station_list.return_value = "station_list"

    from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline
    pipeline = WscHydrometricPipeline(db_conn="FakeDBConnection", date_now=pendulum.now("UTC"))

    # Case 1: No data Downloaded
    with pytest.raises(RuntimeError, match=".*__downloaded_data is empty.*"):
        pipeline.transform_data()

    # Case 2: Data downloaded but wrong filename
    pipeline._EtlPipeline__downloaded_data["wrong_filename.csv"] =  pl.LazyFrame()

    with pytest.raises(KeyError, match=".*get the downloaded data.*"):
        pipeline.transform_data()

    # Case 3: Correct filename and download but common transformations fail due to missing column
    pipeline.station_list = transform_case_station_id
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] =  transform_case_3

    ## Call transform_data
    with pytest.raises(pl.exceptions.ColumnNotFoundError):
        pipeline.transform_data()


    # Case 4: station_id_list is not a LazyFrame
    pipeline.station_list = "station_list"
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] = transform_case_4

    with pytest.raises(TypeError, match=".*station_list was not a LazyFrame.*"):
        pipeline.transform_data()

    # Case 5: Null in values
    pipeline.station_list = transform_case_station_id
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] =  transform_case_5

    pipeline.transform_data()

    level_data = pipeline._EtlPipeline__transformed_data["level"]["df"].sort(["station_id", "datestamp"])
    discharge_data = pipeline._EtlPipeline__transformed_data["discharge"]["df"].sort(["station_id", "datestamp"])


    ## Check column names and dtypes
    level_columns = level_data.columns
    level_dtypes = level_data.dtypes
    discharge_columns = discharge_data.columns
    discharge_dtypes = discharge_data.dtypes

    assert level_columns == ['station_id', 'variable_id', 'datestamp', 'value', 'qa_id']
    assert level_dtypes == [pl.Int64, pl.Int8, pl.Date, pl.Float64, pl.Int8]
    assert discharge_columns == ['station_id', 'variable_id', 'datestamp', 'value', 'qa_id']
    assert discharge_dtypes == [pl.Int64, pl.Int8, pl.Date, pl.Float64, pl.Int8]

    ## Check shape of dataframes
    assert level_data.shape == (3, 5)
    assert discharge_data.shape == (2, 5)

    ## Check Values
    assert np.all(level_data.select("qa_id").to_numpy() == 0)
    assert np.all(discharge_data.select("qa_id").to_numpy() == 0)
    assert np.all(level_data.select("variable_id").to_numpy() == 2)
    assert np.all(discharge_data.select("variable_id").to_numpy() == 1)

    # Case 6: Successful transformation
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] = transform_case_4

    pipeline.transform_data()
    level_data = pipeline._EtlPipeline__transformed_data["level"]["df"].sort(["station_id", "datestamp"])
    discharge_data = pipeline._EtlPipeline__transformed_data["discharge"]["df"].sort(["station_id", "datestamp"])

    ## Check column names and dtypes
    level_columns = level_data.columns
    level_dtypes = level_data.dtypes
    discharge_columns = discharge_data.columns
    discharge_dtypes = discharge_data.dtypes

    assert level_columns == ['station_id', 'variable_id', 'datestamp', 'value', 'qa_id']
    assert level_dtypes == [pl.Int64, pl.Int8, pl.Date, pl.Float64, pl.Int8]
    assert discharge_columns == ['station_id', 'variable_id', 'datestamp', 'value', 'qa_id']
    assert discharge_dtypes == [pl.Int64, pl.Int8, pl.Date, pl.Float64, pl.Int8]

    ## Check shape of dataframes
    assert level_data.shape == (4, 5)
    assert discharge_data.shape == (4, 5)

    ## Check Values
    assert np.all(level_data.select("qa_id").to_numpy() == 0)
    assert np.all(discharge_data.select("qa_id").to_numpy() == 0)
    assert np.all(level_data.select("variable_id").to_numpy() == 2)
    assert np.all(discharge_data.select("variable_id").to_numpy() == 1)

    level_rows = level_data.select("station_id", "datestamp", "value").rows()
    discharge_rows = discharge_data.select("station_id", "datestamp", "value").rows()
    ids = [123, 456]
    values = [2.5, 5.0, 7.5, 10.0]

    for i in range(4):
        level_rows[i][0] == ids[i%2]
        level_rows[i][1] == pendulum.date(2025, 4, 16).subtract(days=i%2)
        level_rows[i][2] == values[i]
        discharge_rows[i][0] == ids[i%2]
        discharge_rows[i][1] == pendulum.date(2025, 4, 16).subtract(days=i%2)
        discharge_rows[i][2] == values[i]

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.get_station_list")
def test_validate_downloaded_data(mock_get_station_list):
    mock_get_station_list.return_value = "station_list"

    from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline
    pipeline = WscHydrometricPipeline(db_conn="FakeDBConnection", date_now=pendulum.now("UTC"))

    # Case 1: No data Downloaded
    pipeline._EtlPipeline__downloaded_data = {}

    with pytest.raises(ValueError):
        pipeline.validate_downloaded_data()

    # Case 2: Data Downloaded but wrong columns
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] = validate_data_case_2

    with pytest.raises(ValueError):
        pipeline.validate_downloaded_data()

    # Case 3: Data Downloaded but wrong types
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] = validate_data_case_3

    with pytest.raises(TypeError):
        pipeline.validate_downloaded_data()

    #Case 4: Data Downloaded and correct
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] = validate_data_case_4

    pipeline.validate_downloaded_data()
