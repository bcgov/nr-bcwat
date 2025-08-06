import polars as pl
import datetime
from utils.climate import (
    generate_climate_precipitation_yearly_metrics,
    generate_climate_station_metrics,
    generate_current_precipitation,
    generate_current_temperature,
    generate_historical_precipitation
)
from freezegun import freeze_time

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

@freeze_time('2020-01-01')
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
    assert len(temperature_current_1) == 366

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

@freeze_time("2020-01-03")
def test_generate_current_precipitation():
    # Empty input
    precip_metrics_1 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 27, "value": 3, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )

    results = generate_current_precipitation(precip_metrics_1)
    assert results[0]['d'].year == 2019
    assert results[0]['d'].month == 1
    assert results[0]['d'].day == 1
    for result in results:
        date = result['d']
        if(date.year == 2019):
            assert result['v'] == None
        else:
            if(date.day == 1):
                assert result['v'] == 1
            if(date.day == 2):
                assert result['v'] == 6
            if(date.day == 3):
                assert result['v'] == 9

    # Ensure old data isn't taken into account
    precip_metrics_1 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2018, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2018, 1, 2), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2018, 1, 3), "variable_id": 27, "value": 3, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 27, "value": 3, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )

    results = generate_current_precipitation(precip_metrics_1)
    assert results[0]['d'].year == 2019
    assert results[0]['d'].month == 1
    assert results[0]['d'].day == 1
    for result in results:
        date = result['d']
        if(date.year == 2019):
            assert result['v'] == None
        else:
            if(date.day == 1):
                assert result['v'] == 1
            if(date.day == 2):
                assert result['v'] == 6
            if(date.day == 3):
                assert result['v'] == 9

    # Ensure old data isn't taken into account
    precip_metrics_1 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2019, 12, 29), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 12, 30), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 12, 31), "variable_id": 27, "value": 3, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 27, "value": 3, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )

    results = generate_current_precipitation(precip_metrics_1)
    assert results[0]['d'].year == 2019
    assert results[0]['d'].month == 1
    assert results[0]['d'].day == 1
    for result in results:
        date = result['d']
        if(date.year == 2019):
            if(date.month == 12):
                if(date.day == 29):
                    assert result['v'] == 1
                elif(date.day == 30):
                    assert result['v'] == 6
                elif(date.day == 31):
                    assert result['v'] == 9
                else:
                    assert result['v'] == None
            else:
                assert result['v'] == None
        else:
            if(date.day == 1):
                assert result['v'] == 1
            if(date.day == 2):
                assert result['v'] == 6
            if(date.day == 3):
                assert result['v'] == 9

def test_generate_historical_precipitation():
    """
        Generate historical precipitation with monthly quantiles
    """
    # One entry for each month, should be simple calculation
    precip_metrics_1 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 2, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 3, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 4, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 5, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 6, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 7, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 8, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 9, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 10, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 11, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 12, 1), "variable_id": 27, "value": 1, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )
    results = generate_historical_precipitation(precip_metrics_1)
    index = 1
    for result in results:
        assert result['d'] == index
        assert result['p90'] == 1
        assert result['p75'] == 1
        assert result['p50'] == 1
        assert result['p25'] == 1
        assert result['p10'] == 1
        index += 1

    # Have 5 entries to fill up the quantile calculation in January
    precip_metrics_1 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 1, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2018, 1, 1), "variable_id": 27, "value": 3, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2017, 1, 1), "variable_id": 27, "value": 4, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2016, 1, 1), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 2, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 3, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 4, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 5, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 6, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 7, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 8, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 9, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 10, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 11, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 12, 1), "variable_id": 27, "value": 1, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )
    results = generate_historical_precipitation(precip_metrics_1)
    index = 1
    for result in results:
        assert result['d'] == index
        if(index <= 31):
            # January
            assert result['p90'] == 5
            assert result['p75'] == 4
            assert result['p50'] == 3
            assert result['p25'] == 2
            assert result['p10'] == 1

        else:
            assert result['p90'] == 1
            assert result['p75'] == 1
            assert result['p50'] == 1
            assert result['p25'] == 1
            assert result['p10'] == 1
        index += 1

    # Make the same as the above but generated because of summing months instead of a single value
    # Same entry values should double the outputs
    precip_metrics_1 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 1, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2018, 1, 1), "variable_id": 27, "value": 3, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2017, 1, 1), "variable_id": 27, "value": 4, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2016, 1, 1), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 1, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2018, 1, 1), "variable_id": 27, "value": 3, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2017, 1, 1), "variable_id": 27, "value": 4, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2016, 1, 1), "variable_id": 27, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 2, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 3, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 4, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 5, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 6, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 7, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 8, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 9, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 10, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 11, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 12, 1), "variable_id": 27, "value": 1, "survey_period": None}
        ],
        schema_overrides={
            "station_id": pl.Int32,
            "datestamp": pl.Date,
            "variable_id": pl.Int16,
            "value": pl.Float64,
            "survey_period": pl.String
        }
    )
    results = generate_historical_precipitation(precip_metrics_1)
    index = 1
    for result in results:
        assert result['d'] == index
        if(index <= 31):
            # January
            assert result['p90'] == 10
            assert result['p75'] == 8
            assert result['p50'] == 6
            assert result['p25'] == 4
            assert result['p10'] == 2

        else:
            assert result['p90'] == 1
            assert result['p75'] == 1
            assert result['p50'] == 1
            assert result['p25'] == 1
            assert result['p10'] == 1
        index += 1

def test_generate_climate_precipitation_yearly_metrics():
    """
        Function aggregates values into monthly sums and treats that value as the same for each ordinal day
    """
    # aggregate them all into the 1 for each month
    precip_metrics_1 = [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 2, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 3, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 4, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 5, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 6, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 7, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 8, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 9, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 10, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 11, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 12, 1), "variable_id": 27, "value": 1, "survey_period": None}
        ]

    results = generate_climate_precipitation_yearly_metrics(precip_metrics_1, 2020)
    index = 1
    for result in results:
        assert result['d'] == index
        assert result['v'] == 1
        index += 1

    # ensure old years aren't taken into account
    precip_metrics_1 = [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 1, 1), "variable_id": 27, "value": 100, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 2, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 3, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 4, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 5, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 6, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 7, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 8, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 9, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 10, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 11, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 12, 1), "variable_id": 27, "value": 1, "survey_period": None}
        ]

    results = generate_climate_precipitation_yearly_metrics(precip_metrics_1, 2020)
    index = 1
    for result in results:
        assert result['d'] == index
        assert result['v'] == 1
        index += 1

    # ensure sums for each month month are taken into account
    precip_metrics_1 = [
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 2, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 2, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 3, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 3, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 4, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 4, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 5, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 5, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 6, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 6, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 7, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 7, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 8, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 8, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 9, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 9, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 10, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 10, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 11, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 11, 1), "variable_id": 27, "value": 2, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 12, 1), "variable_id": 27, "value": 1, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2020, 12, 1), "variable_id": 27, "value": 2, "survey_period": None}
        ]

    results = generate_climate_precipitation_yearly_metrics(precip_metrics_1, 2020)
    index = 1
    for result in results:
        assert result['d'] == index
        assert result['v'] == 3
        index += 1


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

