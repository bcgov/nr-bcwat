from utils.climate import (
    generate_climate_station_metrics,
    generate_current_temperature,
    generate_historical_temperature,
    generate_current_precipitation,
    generate_historical_precipitation,
    generate_current_snow_on_ground_depth,
    generate_historical_snow_on_ground_depth,
    generate_current_snow_water_equivalent,
    generate_historical_snow_water_equivalent,
    generate_current_manual_snow_survey,
    generate_historical_manual_snow_survey
)

from tests.unit.fixtures.climate.utils.station_16831_metrics_raw import station_16831_metrics_raw
from tests.unit.fixtures.climate.utils.station_16831_metrics_computed import station_16831_metrics_computed

def test_generate_climate_station_metrics():
    # Generic Test - Full Station
    computed_metrics = generate_climate_station_metrics(station_16831_metrics_raw)
    assert computed_metrics == station_16831_metrics_computed

    # Tests of individual functions will be performed below, using obvious metrics for determining metrics

def test_generate_current_temperature():
    assert True

def test_generate_historical_temperature():
    assert True

def test_generate_current_precipitation():
    assert True

def test_generate_historical_precipitation():
    assert True

def test_generate_current_snow_on_ground_depth():
    assert True

def test_generate_historical_snow_on_ground_depth():
    assert True

def test_generate_current_snow_water_equivalent():
    assert True

def test_generate_historical_snow_water_equivalent():
    assert True

def test_generate_current_manual_snow_survey():
    assert True

def test_generate_historical_manual_snow_survey():
    assert True

