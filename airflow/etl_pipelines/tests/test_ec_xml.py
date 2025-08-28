from etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml import EcXmlPipeline
from etl_pipelines.utils.constants import(
    EC_XML_BASE_URL,
    EC_XML_DESTINATION_TABLES,
    EC_XML_DTYPE_SCHEMA,
    EC_XML_MIN_RATIO,
    EC_XML_NAME,
    EC_XML_NETWORK_ID,
    EC_XML_RENAME_DICT,
    EC_XML_STATION_SOURCE
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

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml.pl.read_database")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_initialization(
    fake_get_station_list
):
    # Set up fakes
    # EC XML scrapers use the same stations as the climate_ec_update quarterly scraper
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = EcXmlPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Assertion time
    assert pipeline.name == EC_XML_NAME
    assert pipeline.source_url == {
        '20250826': 'https://dd.meteo.gc.ca/20250826/WXO-DD/observations/xml/BC/yesterday/yesterday_bc_20250826_e.xml',
        '20250827': 'https://dd.meteo.gc.ca/20250827/WXO-DD/observations/xml/BC/yesterday/yesterday_bc_20250827_e.xml'
    }
    assert pipeline.destination_tables == EC_XML_DESTINATION_TABLES
    assert pipeline.days == 3
    assert pipeline.station_source == EC_XML_STATION_SOURCE
    assert pipeline.expected_dtype == EC_XML_DTYPE_SCHEMA
    assert pipeline.column_rename_dict == EC_XML_RENAME_DICT
    assert pipeline.go_through_all_stations
    assert pipeline.overrideable_dtype
    assert pipeline.network == EC_XML_NETWORK_ID
    assert pipeline.min_ratio == EC_XML_MIN_RATIO
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
            day=pendulum.now("UTC").day,
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
            day=pendulum.now("UTC").day-3,
            hour=pendulum.now("UTC").hour,
            second=pendulum.now("UTC").second,
            time_zone=str(pendulum.now("UTC").tz)
        ))
    )

    plt.assert_frame_equal(
        pipeline.station_list,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_station.csv",
            has_header=True,
            schema_overrides={
                "original_id": pl.String,
                "station_id": pl.Int64
            }
        )
    )
    assert True

@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml.pl.read_database")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_make_polars_dataframe(
    fake_get_station_list,
    fake_logger
):
    # Set up fakes
    # EC XML scrapers use the same stations as the climate_ec_update quarterly scraper
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = EcXmlPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Fail because the response.text is empty
    response_text = PropertyMock(return_value=None)
    fake_response = MagicMock()

    type(fake_response).text = response_text

    with pytest.raises(RuntimeError, match="The downloaded data was empty! Exiting and flagging as failure."):
        pipeline._StationObservationPipeline__make_polars_lazyframe(fake_response, "test_id")

    fake_logger.info.assert_called_once_with("Decoding XML data")
    fake_logger.error.assert_called_once_with("The downloaded data was empty! Exiting and flagging as failure.")

    # Clean Up
    fake_logger.reset_mock()

    # Fail in loading block case
    response_text = PropertyMock(return_value="<om:ObservationCollection><om:member></om:member></om:ObservationCollection>")
    fake_response = MagicMock()

    type(fake_response).text = response_text

    with pytest.raises(RuntimeError, match=rf"Failed to transform the XML data in to a polars LazyFrame.*"):
        pipeline._StationObservationPipeline__make_polars_lazyframe(fake_response, "test_id")

    fake_logger.info.assert_called_once_with("Decoding XML data")
    fake_logger.error.assert_called_once_with(Contains(f"Failed to transform the XML data in to a polars LazyFrame."), exc_info=True)

    # Clean up
    fake_logger.reset_mock()

    # Success Case
    response_text = PropertyMock(return_value=open("etl_pipelines/tests/test_constants/station_csv/ec_xml_raw_download.csv", "r").read())
    fake_response = MagicMock()

    type(fake_response).text = response_text

    output_df = pipeline._StationObservationPipeline__make_polars_lazyframe(fake_response, "test_id")

    fake_logger.info.assert_any_call("Decoding XML data")
    fake_logger.info.assert_any_call("Finished decoding and converting XML data into polars LazyFrame.")
    fake_logger.error.assert_not_called()

    assert fake_logger.info.call_count == 2

    plt.assert_frame_equal(
        output_df,
        pl.scan_csv(
            "etl_pipelines/tests/test_constants/station_csv/ec_xml_download.csv",
            has_header=True,
            null_values=[""],
            schema_overrides={
                'station_name': pl.String,
                'latitude': pl.String,
                'longitude': pl.String,
                'transport_canada_id': pl.String,
                'obs_date_utc': pl.String,
                'obs_date_local': pl.String,
                'climate_stn_num': pl.String,
                'wmo_stn_num': pl.String,
                'air_temp_yesterday_high': pl.String,
                'air_temp_yesterday_low': pl.String,
                'total_precip': pl.String,
                'rain_amnt': pl.String,
                'snow_amnt': pl.String,
                'wind_spd': pl.String,
                'wind_dir': pl.String
            }
        ),
        check_column_order=False,
        check_row_order=False

    )

@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_new_station_in_bc")
@patch("etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline.StationObservationPipeline.check_for_new_stations")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml.logger")
@patch("etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml.pl.read_database")
@freeze_time("2025-08-28 00:00:00 UTC")
def test_transform_data(
    fake_get_station_list,
    fake_logger,
    fake_check_for_new_stations,
    fake_check_new_station_in_bc
):
    # Set up fakes
    # EC XML scrapers use the same stations as the climate_ec_update quarterly scraper
    fake_get_station_list.return_value = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/climate_ec_update_station.csv",
        has_header=True,
        schema_overrides={
            "original_id": pl.String,
            "station_id": pl.Int64
        }
    )

    # Initialize Pipeline
    pipeline = EcXmlPipeline(db_conn = MockDbConn(), date_now = pendulum.now("UTC"))

    # Fails due to empty __downloaded_data case
    with pytest.raises(RuntimeError, match=f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting"):
        pipeline.transform_data()

    fake_logger.info.assert_called_once_with(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.error.assert_called_once_with(f"No data was downloaded for {pipeline.name}! The attribute __downloaded_data is empty. Exiting")

    # Clean up
    fake_logger.reset_mock()

    # Check for new stations fails case
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ec_xml_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=EC_XML_DTYPE_SCHEMA["station_data"]
    ).head(0)

    fake_check_for_new_stations.side_effect = Exception("Error")

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains(f"Failed to check for new stations in the data for {pipeline.name}."))
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")

    assert fake_logger.info.call_count == 2

    # Clean Up
    fake_logger.reset_mock()
    fake_check_for_new_stations.reset_mock(side_effect=True)

    # No new stations were found case
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id": []})

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.info.assert_any_call(f"No new stations were found in the downloaded data for {pipeline.name}. Continuing on")
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")
    fake_logger.error.assert_not_called()

    assert fake_logger.info.call_count == 3

    # Clean Up
    fake_logger.reset_mock()

    # Fails checking if new station is in BC Case
    fake_check_for_new_stations.return_value = pl.LazyFrame({"original_id": ["test_id"]})
    fake_check_new_station_in_bc.side_effect = Exception("Error")

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.error.assert_called_once_with(Contains(f"Failed to check for new stations in the data for {pipeline.name}."))
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")

    assert fake_logger.info.call_count == 2


    # Clean Up
    fake_logger.reset_mock()
    fake_check_new_station_in_bc.reset_mock(side_effect=True)

    # Case where new station exists but not in BC
    fake_check_new_station_in_bc.return_value = []

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.info.assert_any_call("There were new stations, but they are not within BC. Moving on without notifying.")
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")
    fake_logger.error.assert_not_called()

    assert fake_logger.info.call_count == 3

    # Clean Up
    fake_logger.reset_mock()

    # Case where new station exists in BC
    fake_check_new_station_in_bc.return_value = ["test_id"]

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.warning.assert_called_once_with(Contains(f"New stations were found while checking the data that was downloaded for {pipeline.name}."))
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")
    fake_logger.error.assert_not_called()

    assert fake_logger.info.call_count == 2

    # Clean Up
    fake_logger.reset_mock()

    # Failure in the transform block
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.LazyFrame({"climate_stn_num":[], "longitude":[], "latitude":[]})

    with pytest.raises(RuntimeError, match=rf"Error when trying to transform the data for {pipeline.name}.*"):
        pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.warning.assert_called_once_with(Contains(f"New stations were found while checking the data that was downloaded for {pipeline.name}."))
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.error.assert_called_once_with(Contains(f"Error when trying to transform the data for {pipeline.name}."), exc_info=True)

    # Clean Up
    fake_logger.reset_mock()

    # Success!
    pipeline._EtlPipeline__downloaded_data["station_data"] = pl.scan_csv(
        "etl_pipelines/tests/test_constants/station_csv/ec_xml_download.csv",
        has_header=True,
        null_values=[""],
        schema_overrides=EC_XML_DTYPE_SCHEMA["station_data"]
    )

    pipeline.transform_data()

    fake_logger.info.assert_any_call(f"Transforming downloaded data for {pipeline.name}")
    fake_logger.warning.assert_called_once_with(Contains(f"New stations were found while checking the data that was downloaded for {pipeline.name}."))
    fake_logger.debug.assert_called_once_with(f"Starting Transformation")
    fake_logger.info.assert_any_call(f"Finished Transforming data for {pipeline.name}")
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
                "etl_pipelines/tests/test_constants/station_csv/ec_xml_output.csv",
                has_header=True,
                null_values=[""],
                schema_overrides={
                    'datestamp': pl.Date,
                    'station_id': pl.Int64,
                    'variable_id': pl.Int32,
                    'qa_id': pl.Int32,
                    'value': pl.Float64
                }
            )
        ),
        check_column_order=False,
        check_row_order=False
    )
