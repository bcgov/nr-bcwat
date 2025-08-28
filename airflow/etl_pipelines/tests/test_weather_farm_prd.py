from etl_pipelines.scrapers.StationObservationPipeline.climate.weather_farm_prd import WeatherFarmPrdPipeline
from etl_pipelines.utils.constants import(
    WEATHER_FARM_PRD_BASE_URL,
    WEATHER_FARM_PRD_DESTINATION_TABLES,
    WEATHER_FARM_PRD_DTYPE_SCHEMA,
    WEATHER_FARM_PRD_MIN_RATIO,
    WEATHER_FARM_PRD_NAME,
    WEATHER_FARM_PRD_NETWORK_ID,
    WEATHER_FARM_PRD_RENAME_DICT,
    WEATHER_FARM_PRD_STATION_SOURCE
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

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.weather_farm_prd.pl.read_database")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_initialization(fake_get_station_list):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/weather_farm_prd_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = WeatherFarmPrdPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == WEATHER_FARM_PRD_NAME
    assert pipeline.source_url == {
        '54d02480-82b1-4914-2761-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=54d02480-82b1-4914-2761-08d6b85b0e2d&TimeInterval=day',
        '9a90c322-8cc7-41c6-2768-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=9a90c322-8cc7-41c6-2768-08d6b85b0e2d&TimeInterval=day',
        '6272638b-827b-4e87-2769-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=6272638b-827b-4e87-2769-08d6b85b0e2d&TimeInterval=day',
        '54f874d9-b542-40dd-2766-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=54f874d9-b542-40dd-2766-08d6b85b0e2d&TimeInterval=day',
        'c5c3f303-9915-4b78-276d-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=c5c3f303-9915-4b78-276d-08d6b85b0e2d&TimeInterval=day',
        'cbffd91f-8c45-413b-2765-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=cbffd91f-8c45-413b-2765-08d6b85b0e2d&TimeInterval=day',
        '200ac41d-4dcd-49e8-276e-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=200ac41d-4dcd-49e8-276e-08d6b85b0e2d&TimeInterval=day',
        'cb710608-265d-4ad3-275b-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=cb710608-265d-4ad3-275b-08d6b85b0e2d&TimeInterval=day',
        'fc330dba-2c2e-4168-275c-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=fc330dba-2c2e-4168-275c-08d6b85b0e2d&TimeInterval=day',
        'f9f4606e-ba12-49bc-2764-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=f9f4606e-ba12-49bc-2764-08d6b85b0e2d&TimeInterval=day',
        '0c3a73c3-1b30-4bf4-276b-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=0c3a73c3-1b30-4bf4-276b-08d6b85b0e2d&TimeInterval=day',
        'd1501989-7b3f-4dcb-275f-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=d1501989-7b3f-4dcb-275f-08d6b85b0e2d&TimeInterval=day',
        'd61e5388-a8c6-4dad-2763-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=d61e5388-a8c6-4dad-2763-08d6b85b0e2d&TimeInterval=day',
        'f496492a-25b1-4c4c-2767-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=f496492a-25b1-4c4c-2767-08d6b85b0e2d&TimeInterval=day',
        'f17b76d1-0b03-4a70-2760-08d6b85b0e2d': 'http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate=2025-08-25&EndDate=2025-08-29&StationId=f17b76d1-0b03-4a70-2760-08d6b85b0e2d&TimeInterval=day'}
    assert pipeline.destination_tables == WEATHER_FARM_PRD_DESTINATION_TABLES
    assert pipeline.days == 3
    assert pipeline.station_source == WEATHER_FARM_PRD_STATION_SOURCE
    assert pipeline.expected_dtype == WEATHER_FARM_PRD_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == WEATHER_FARM_PRD_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == WEATHER_FARM_PRD_NETWORK_ID
    assert pipeline.min_ratio == WEATHER_FARM_PRD_MIN_RATIO
    assert pipeline.file_encoding == "utf8"
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}
    assert pipeline.date_now == pendulum.now("UTC")

    plt.assert_frame_equal(
        pl.select(pipeline.end_date),
        pl.select(pl.datetime(
            year=pendulum.now("UTC").year,
            month=pendulum.now("UTC").month,
            day=pendulum.now("UTC").add(days=1).day,
            hour=pendulum.now("UTC").hour,
            second=pendulum.now("UTC").second,
            time_zone=str(pendulum.now("UTC").tz)
        ))
    )
    plt.assert_frame_equal(
        pl.select(pipeline.start_date),
        pl.select(pl.datetime(
            year=pendulum.now("UTC").year,
            month=pendulum.now("UTC").month,
            day=pendulum.now("UTC").subtract(days=3).day,
            hour=pendulum.now("UTC").hour,
            second=pendulum.now("UTC").second,
            time_zone=str(pendulum.now("UTC").tz)
        ))
    )

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/weather_farm_prd_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.weather_farm_prd.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.weather_farm_prd.pl.read_database")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_transform_data(
    fake_get_station_list,
    fake_logger
):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/weather_farm_prd_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = WeatherFarmPrdPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where there is no data in __downloaded_data
    with pytest.raises(RuntimeError, match=f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.error.assert_called_once_with(f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting")

    # Clean Up
    fake_logger.reset_mock()

    # Case where it fails in the transformation block
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame()

    with pytest.raises(RuntimeError, match=rf"Error when trying to transform the data for {pipeline.name}.*"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.error.assert_called_once_with(Contains(f"Error when trying to transform the data for {pipeline.name}."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Success Case
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/weather_farm_prd_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=WEATHER_FARM_PRD_DTYPE_SCHEMA["station_data"]
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transformation for {pipeline.name}")
    fake_logger.error.assert_not_called()

    assert fake_logger.info.call_count == 2
    assert len(pipeline._EtlPipeline__transformed_data.keys()) == 1
    assert set(pipeline._EtlPipeline__transformed_data.keys()) == {"station_data"}
    assert pipeline._EtlPipeline__transformed_data["station_data"]["pkey"] == ["station_id", "datestamp", "variable_id"]
    assert not pipeline._EtlPipeline__transformed_data["station_data"]["truncate"]

    plt.assert_frame_equal(
        pipeline._EtlPipeline__transformed_data["station_data"]["df"],
        (
            pl.read_csv(
                "etl_pipelines/tests/test_constants/station_csv/weather_farm_prd_output.csv",
                has_header=True,
                null_values=[""],
                schema_overrides={
                    'station_id': pl.Int64,
                    'variable_id': pl.Int32,
                    'datestamp': pl.Date,
                    'value': pl.Float64,
                    'qa_id': pl.Int32
                }
            )
        ),
        check_column_order=False,
        check_row_order=False
    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.weather_farm_prd.pl.read_database")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_make_polars_lazyframe(
    fake_get_station_list
):
    # Set up mocks
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/weather_farm_prd_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = WeatherFarmPrdPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Case where downloaded data was empty
    raw_text = PropertyMock(
        return_value='[]'
    )
    fake_response = MagicMock()

    type(fake_response).text = raw_text

    with pytest.raises(ValueError, match="There is no data in the station. Continuing but marking as failure"):
        pipeline._StationObservationPipeline__make_polars_lazyframe(fake_response, "test_id")

    # Success case
    raw_text = PropertyMock(
        return_value='[{"accumPrecip":0,"ytdPrecip":178.81599999999995,"dateTimeStamp":"2025-08-25T00:00:00","frostFreeDays":0},{"accumPrecip":0,"ytdPrecip":178.81599999999995,"dateTimeStamp":"2025-08-26T00:00:00","frostFreeDays":0},{"accumPrecip":0,"ytdPrecip":178.81599999999995,"dateTimeStamp":"2025-08-27T00:00:00","frostFreeDays":0},{"accumPrecip":0,"ytdPrecip":178.81599999999995,"dateTimeStamp":"2025-08-28T00:00:00","frostFreeDays":0},{"accumPrecip":0,"ytdPrecip":178.81599999999995,"dateTimeStamp":"2025-08-29T00:00:00","frostFreeDays":0}]'
    )
    fake_response = MagicMock()

    type(fake_response).text = raw_text

    output_df = pipeline._StationObservationPipeline__make_polars_lazyframe(fake_response, "test_id")

    plt.assert_frame_equal(
        output_df,
        pl.LazyFrame(
            {
                "original_id": ['test_id','test_id','test_id','test_id','test_id'],
                "dateTimeStamp": ['2025-08-25T00:00:00','2025-08-26T00:00:00','2025-08-27T00:00:00','2025-08-28T00:00:00','2025-08-29T00:00:00'],
                "accumPrecip": [0.0,0.0,0.0,0.0,0.0],
                "ytdPrecip": [178.81599999999995,178.81599999999995,178.81599999999995,178.81599999999995,178.81599999999995],
                "rainfall": [None,None,None,None,None],
                "humidityOut": [None,None,None,None,None],
                "tempMax": [None,None,None,None,None],
                "tempMin": [None,None,None,None,None],
                "tempAvg": [None,None,None,None,None],
                "windChill": [None,None,None,None,None],
                "windPrevailDir": [None,None,None,None,None],
                "windspeedAvg": [None,None,None,None,None],
                "windspeedHigh": [None,None,None,None,None],
                "frostFreeDays": [0,0,0,0,0]
            },
            schema_overrides=WEATHER_FARM_PRD_DTYPE_SCHEMA["station_data"]
        )
    )

