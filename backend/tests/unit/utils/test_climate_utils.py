import polars as pl
import datetime
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

from pathlib import Path
from pprint import pformat

def test_generate_climate_station_metrics(app):
    """
        General Unit Test of Generating Climate Station Metrics.

        Testing 3 Stations, each of which tracking different variables.

        Sub Tests, for the simple sub functions, are performed below.
    """

    # Generic Test - Full Station
    raw_metrics = app.db.get_climate_station_report_by_id(station_id=1)
    computed_metrics = generate_climate_station_metrics(raw_metrics)

    # Precip/Temperature/SnowDepth
    from fixtures.climate.station_1_metrics_computed import station_1_metrics_computed
    assert computed_metrics == station_1_metrics_computed

    raw_metrics = app.db.get_climate_station_report_by_id(station_id=287)
    computed_metrics = generate_climate_station_metrics(raw_metrics)

    # Snow Equivalent
    from fixtures.climate.station_287_metrics_computed import station_287_metrics_computed
    assert computed_metrics == station_287_metrics_computed

    raw_metrics = app.db.get_climate_station_report_by_id(station_id=17401)
    computed_metrics = generate_climate_station_metrics(raw_metrics)

    # Manual Snow Survey
    from fixtures.climate.station_17401_metrics_computed import station_17401_metrics_computed
    assert computed_metrics == station_17401_metrics_computed

# Tests of individual functions will be performed below, using obvious metrics for determining metrics


def test_generate_current_temperature():
    """
        Unit Tests of validating calculations for generating current temperature.

        Very simple function, focused on determining the Max/Min readings of variable_ids 6/8 per day.

        The tests below focus on simple validation of:
            - Group By Functionality (datestamps)
            - Filter Out unused variable_ids
            - Null Entry Handling
    """

    temperature_metrics_1 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 7, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 3, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )

    temperature_current_1 = generate_current_temperature(temperature_metrics_1)


    # Validate Column names of output dictionary
    expected_keys = {"d", "max", "min"}
    assert set(temperature_current_1[0].keys()) == expected_keys, f"Unexpected keys: {temperature_current_1[0].keys()}"

    # Validating taking the Max of correct variable_ids, omitting variable_id 7
    assert temperature_current_1[0]['max'] == 1
    assert temperature_current_1[0]['min'] == 3

    # Validate Length = 1 (Grouping By Datestamp Properly)
    assert len(temperature_current_1) == 1

    temperature_metrics_2 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 8, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 8, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )

    temperature_current_2 = generate_current_temperature(temperature_metrics_2)

    # Validate Max/Min Proper for Variable Id
    assert temperature_current_2[0]['max'] == 8
    assert temperature_current_2[0]['min'] == 5

    # Validate Length = 1 (One Row per Datestamp)
    assert len(temperature_current_2) == 1

    temperature_metrics_3 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 7, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 8, "value": 7, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 8, "value": 7, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 8, "value": 7, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 5), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 5), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 5), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 5), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 5), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 5), "variable_id": 8, "value": 7, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 6), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 6), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 6), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 6), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 6), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 6), "variable_id": 8, "value": 7, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 7), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 7), "variable_id": 8, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 7), "variable_id": 6, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 7), "variable_id": 8, "value": 6, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 7), "variable_id": 6, "value": 7, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 7), "variable_id": 8, "value": 7, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )

    temperature_current_3 = generate_current_temperature(temperature_metrics_3)

    # Simple Validation of Max Calculation, Sort By
    prev_row = datetime.date(2019, 12, 31)
    for row in temperature_current_3:
        assert row['min'] == 5
        assert row['max'] == 7
        assert row['d'] > prev_row
        prev_row = row['d']

    # Validate Length = 7 (One Row per Datestamp)
    assert len(temperature_current_3) == 7

    temperature_metrics_4 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": None, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 6, "value": None, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 8, "value": 5, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 6, "value": None, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 8, "value": None, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 6, "value": 5, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 5), "variable_id": 8, "value": 5, "survey_period": None}


        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )

    temperature_current_4 = generate_current_temperature(temperature_metrics_4)

    # Validate Null Handling (Explicit & Missing)
    assert temperature_current_4[0]['max'] is not None
    assert temperature_current_4[0]['min'] is None

    assert temperature_current_4[1]['max'] is None
    assert temperature_current_4[1]['min'] is not None

    assert temperature_current_4[2]['max'] is None
    assert temperature_current_4[2]['min'] is None

    assert temperature_current_4[3]['max'] is not None
    assert temperature_current_4[3]['min'] is None

    assert temperature_current_4[4]['max'] is None
    assert temperature_current_4[4]['min'] is not None

def test_generate_historical_temperature():
    assert False

def test_generate_current_precipitation():
    assert False

def test_generate_historical_precipitation():
    assert False

def test_generate_current_snow_on_ground_depth():
    assert False

def test_generate_historical_snow_on_ground_depth():
    assert False

def test_generate_current_snow_water_equivalent():
    assert False

def test_generate_historical_snow_water_equivalent():
    assert False

def test_generate_current_manual_snow_survey():
    assert False

def test_generate_historical_manual_snow_survey():
    assert False

