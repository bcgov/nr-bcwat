from freezegun import freeze_time
from mock import patch
from etl_pipelines.utils.constants import (
    WSC_URL,
    WSC_DESTINATION_TABLES,
    WSC_NAME,
    WSC_DTYPE_SCHEMA,
    WSC_MIN_RATIO,
    WSC_RENAME_DICT,
    WSC_NETWORK,
    WSC_STATION_SOURCE,
)
from etl_pipelines.tests.test_constants.test_wsc_hydrometric_constants import(
    transform_case_2,
    transform_case_3,
    transform_case_4,
    transform_case_5,
    transform_case_station_id,
)
from mock import MagicMock
import polars as pl
import polars.testing as plt
import pytest
import numpy as np
import pendulum

@freeze_time("2025-04-16 00:00:00 UTC")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.get_station_list")
def test_initialization(mock_get_station_list):
    # This mock happens to ensure that the database is not accessed while testing.
    # The function get_station_list is not unique to this pipeline, so it is mocked.
    mock_get_station_list.return_value = None

    # Importing the class has to happen after the patch, or else the get_station_list will be called before it gets patched.
    from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline
    pipeline = WscHydrometricPipeline(db_conn="FakeDBConnection", date_now=pendulum.now("UTC"))

    # Assert initialization attributes for WscHydrometricPipeline class
    assert pipeline.source_url == {"wsc_daily_hydrometric.csv": WSC_URL.format("20250416")}

    # Assert Initialization Attributes for parent class StationObservationPipeline
    assert pipeline.station_list == None
    assert pipeline.all_stations_in_network == None
    assert pipeline.days == 2
    assert pipeline.station_source == "wsc"
    assert pipeline.expected_dtype == WSC_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == WSC_RENAME_DICT
    assert pipeline.go_through_all_stations == False
    assert pipeline.overrideable_dtype == True
    assert pipeline.network == WSC_NETWORK
    assert pipeline.min_ratio == WSC_MIN_RATIO
    assert pipeline.db_conn == "FakeDBConnection"
    assert pipeline.date_now == pendulum.now("UTC")
    assert pl.select(pipeline.end_date)["datetime"][0] == pendulum.now("UTC")
    assert pl.select(pipeline.start_date)["datetime"][0] == pendulum.now("UTC").subtract(days=2)

    # Assert Initialization attributes for parent class EtlPipeline
    assert pipeline.name == WSC_NAME
    assert pipeline.destination_tables == WSC_DESTINATION_TABLES
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.get_station_list")
@freeze_time("2025-04-18 00:00:00 UTC")
def test_transform_data(mock_get_station_list):

    mock_get_station_list.return_value = "station_list"
    db_conn = MagicMock()

    from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline
    pipeline = WscHydrometricPipeline(db_conn=db_conn, date_now=pendulum.now("UTC"))

    # Case 1: No data Downloaded
    with pytest.raises(RuntimeError, match=".*__downloaded_data is empty.*"):
        pipeline.transform_data()

    # Case 2: Data downloaded but wrong filename
    pipeline._EtlPipeline__downloaded_data["wrong_filename.csv"] =  transform_case_2

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

    data = pipeline._EtlPipeline__transformed_data["station_data"]["df"].sort(["station_id", "datestamp"])


    ## Check column names and dtypes
    columns = data.columns
    dtypes = data.dtypes

    assert columns == ['station_id', 'variable_id', 'datestamp', 'value', 'qa_id']
    assert dtypes == [pl.Int64, pl.Int8, pl.Date, pl.Float64, pl.Int8]

    ## Check shape of dataframes
    assert data.shape == (6, 5)

    ## Check Values
    assert np.all(data.select("qa_id").to_numpy() == 0)
    plt.assert_frame_equal(
        data.select("variable_id"),
        pl.DataFrame({"variable_id": [2, 2, 2, 1, 1, 1]}),
        check_row_order=False,
        check_dtypes=False
    )

    # Case 6: Successful transformation
    pipeline._EtlPipeline__downloaded_data["wsc_daily_hydrometric.csv"] = transform_case_4

    pipeline.transform_data()
    data = pipeline._EtlPipeline__transformed_data["station_data"]["df"].sort(["station_id", "datestamp"])

    ## Check column names and dtypes
    columns = data.columns
    dtypes = data.dtypes

    assert columns == ['station_id', 'variable_id', 'datestamp', 'value', 'qa_id']
    assert dtypes == [pl.Int64, pl.Int8, pl.Date, pl.Float64, pl.Int8]

    ## Check shape of dataframes
    assert data.shape == (8, 5)

    ## Check Values
    assert np.all(data.select("qa_id").to_numpy() == 0)
    plt.assert_frame_equal(
        data.select("variable_id"),
        pl.DataFrame({"variable_id": [2, 2, 2, 2, 1, 1, 1, 1]}),
        check_row_order=False,
        check_dtypes=False
    )

    rows = data.select("station_id", "datestamp", "value").rows()
    plt.assert_frame_equal(
        data.select("station_id", "datestamp", "value"),
        pl.DataFrame(
            {
                "station_id": [123,123,123,123,456,456,456,456],
                "datestamp": ["2025-04-16","2025-04-16","2025-04-17","2025-04-17","2025-04-16","2025-04-16","2025-04-17","2025-04-17"],
                "value": [2.0,2.0,4.5,4.5,7.0,7.0,9.5,9.5]
            },
            schema_overrides=({"station_id": pl.Int64, "datestamp": pl.Date, "value": pl.Float64})
        )
    )
