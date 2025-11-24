import polars as pl
import datetime
from utils.climate import (
    generate_climate_precipitation_yearly_metrics,
    generate_historical_temperature,
    generate_climate_station_metrics,
    generate_current_precipitation,
    generate_current_temperature,
    generate_historical_precipitation,
    generate_current_snow_on_ground_depth,
    generate_historical_snow_on_ground_depth,
    generate_current_snow_water_equivalent,
    generate_historical_snow_water_equivalent,
    generate_current_manual_snow_survey,
    generate_historical_manual_snow_survey,
    generate_temperature_yearly_metrics
)
import os
from freezegun import freeze_time

@freeze_time('2025-01-01')
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
    computed_metrics == station_1_metrics_computed

    raw_metrics = app.db.get_climate_station_report_by_id(station_id=287)
    computed_metrics = generate_climate_station_metrics(raw_metrics)

    # Snow Equivalent
    from fixtures.climate.station_287_metrics_computed import station_287_metrics_computed
    for key1 in computed_metrics.keys():
        for key2 in computed_metrics[key1]:
            for i in range(len(computed_metrics[key1][key2])):
                for key3 in computed_metrics[key1][key2][i]:
                    if key1 == "temperature" and key2 == "historical":
                        assert round(computed_metrics[key1][key2][i][key3], 10) == round(station_287_metrics_computed[key1][key2][i][key3], 10)
                    else:
                        assert computed_metrics[key1][key2][i][key3] == station_287_metrics_computed[key1][key2][i][key3]

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
    start_date = datetime.date(2019, 1, 1)
    for i in range(366):
        assert temperature_current_1[i]['d'] == start_date + datetime.timedelta(days = i)
        if(temperature_current_1[i]['d'].year == 2020):
            assert temperature_current_1[i]['max'] == 1
            assert temperature_current_1[i]['min'] == 3
        else:
            assert temperature_current_1[i]['max'] is None
            assert temperature_current_1[i]['min'] is None


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

    # Validating taking the Max of correct variable_ids, omitting variable_id 7
    start_date = datetime.date(2019, 1, 1)
    for i in range(366):
        assert temperature_current_2[i]['d'] == start_date + datetime.timedelta(days = i)
        if(temperature_current_2[i]['d'].year == 2020):
            assert temperature_current_2[i]['max'] == 8
            assert temperature_current_2[i]['min'] == 5
        else:
            assert temperature_current_2[i]['max'] is None
            assert temperature_current_2[i]['min'] is None


    # Validate Length = 1 (Grouping By Datestamp Properly)
    assert len(temperature_current_2) == 366

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
    start_date = datetime.date(2019, 1, 1)
    for i in range(366):
        assert temperature_current_3[i]['d'] == start_date + datetime.timedelta(days = i)
        if(temperature_current_3[i]['d'].year == 2020):
            assert temperature_current_3[i]['max'] == 7
            assert temperature_current_3[i]['min'] == 5
        else:
            assert temperature_current_3[i]['max'] is None
            assert temperature_current_3[i]['min'] is None


    # Validate Length = 7 (One Row per Datestamp)
    # We chop off any days after a certain length
    assert len(temperature_current_3) == 366

    temperature_metrics_4 = pl.LazyFrame(
        [
            {"station_id": 1, "datestamp": datetime.date(2019, 12, 28), "variable_id": 6, "value": 5, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 12, 28), "variable_id": 8, "value": None, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2019, 12, 29), "variable_id": 6, "value": None, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 12, 29), "variable_id": 8, "value": 5, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2019, 12, 30), "variable_id": 6, "value": None, "survey_period": None},
            {"station_id": 1, "datestamp": datetime.date(2019, 12, 30), "variable_id": 8, "value": None, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2019, 12, 31), "variable_id": 6, "value": 5, "survey_period": None},

            {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": 5, "survey_period": None}


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
    assert temperature_current_4[366-5]['max'] is not None
    assert temperature_current_4[366-5]['min'] is None

    assert temperature_current_4[366-4]['max'] is None
    assert temperature_current_4[366-4]['min'] is not None

    assert temperature_current_4[366-3]['max'] is None
    assert temperature_current_4[366-3]['min'] is None

    assert temperature_current_4[366-2]['max'] is not None
    assert temperature_current_4[366-2]['min'] is None

    assert temperature_current_4[366-1]['max'] is None
    assert temperature_current_4[366-1]['min'] is not None

def test_generate_historical_temperature():
    # Single day, one entry for each variable
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 2, "variable_id": 6},
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 8},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datestamp': pl.Date,
            'variable_id': pl.Int16,
            'value': pl.Float64,
            'survey_period': pl.String
    })

    result = generate_historical_temperature(metrics)

    first_day_of_year = result[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['maxp90'] == 2
    assert first_day_of_year['maxavg'] == 2
    assert first_day_of_year['minp10'] == 1
    assert first_day_of_year['minavg'] == 1


    for row in result[1:]:
        assert row['maxp90'] is None
        assert row['maxavg'] is None
        assert row['minp10'] is None
        assert row['minavg'] is None

    # actual quantiles
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 2, "variable_id": 6},
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 8},
        {"datestamp": datetime.date(2024, 1, 1), "value": 3, "variable_id": 6},
        {"datestamp": datetime.date(2024, 1, 1), "value": 0, "variable_id": 8}
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datestamp': pl.Date,
            'variable_id': pl.Int16,
            'value': pl.Float64,
            'survey_period': pl.String
    })

    result = generate_historical_temperature(metrics)

    first_day_of_year = result[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['maxp90'] == 3
    assert first_day_of_year['maxavg'] == 2.5
    assert first_day_of_year['minp10'] == 0
    assert first_day_of_year['minavg'] == 0.5

    for row in result[1:]:
        assert row['maxp90'] is None
        assert row['maxavg'] is None
        assert row['minp10'] is None
        assert row['minavg'] is None


    # actual quantiles on multiple days
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 2, "variable_id": 6},
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 8},
        {"datestamp": datetime.date(2024, 1, 1), "value": 3, "variable_id": 6},
        {"datestamp": datetime.date(2024, 1, 1), "value": 0, "variable_id": 8},
        {"datestamp": datetime.date(2025, 1, 2), "value": 6, "variable_id": 6},
        {"datestamp": datetime.date(2025, 1, 2), "value": 4, "variable_id": 8},
        {"datestamp": datetime.date(2024, 1, 2), "value": 5, "variable_id": 6},
        {"datestamp": datetime.date(2024, 1, 2), "value": 2, "variable_id": 8}
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datestamp': pl.Date,
            'variable_id': pl.Int16,
            'value': pl.Float64,
            'survey_period': pl.String
    })

    result = generate_historical_temperature(metrics)

    first_day_of_year = result[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['maxp90'] == 3
    assert first_day_of_year['maxavg'] == 2.5
    assert first_day_of_year['minp10'] == 0
    assert first_day_of_year['minavg'] == 0.5

    second_day_of_year = result[1]
    assert second_day_of_year['d'] == 2
    assert second_day_of_year['maxp90'] == 6
    assert second_day_of_year['maxavg'] == 5.5
    assert second_day_of_year['minp10'] == 2
    assert second_day_of_year['minavg'] == 3

    for row in result[2:]:
        assert row['maxp90'] is None
        assert row['maxavg'] is None
        assert row['minp10'] is None
        assert row['minavg'] is None

    # full year with actual quantiles
    metrics = []

    index = 0
    while index < 365:
        day_vals = [
            {"datestamp": datetime.date(2025, 1, 1) + datetime.timedelta(days = index), "value": 2 + index, "variable_id": 6},
            {"datestamp": datetime.date(2025, 1, 1) + datetime.timedelta(days = index), "value": 1 + index, "variable_id": 8},
            # 2 non-leap years
            {"datestamp": datetime.date(2023, 1, 1) + datetime.timedelta(days = index), "value": 3 + index, "variable_id": 6},
            {"datestamp": datetime.date(2023, 1, 1) + datetime.timedelta(days = index), "value": 0 + index, "variable_id": 8}
        ]
        metrics.extend(day_vals)
        index = index + 1

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datestamp': pl.Date,
            'variable_id': pl.Int16,
            'value': pl.Float64,
            'survey_period': pl.String
    })

    result = generate_historical_temperature(metrics)


    for index in range(len(result)):
        assert result[index]['d'] == index + 1
        assert result[index]['maxp90'] == 3 + index
        assert result[index]['maxavg'] == 2.5 + index
        assert result[index]['minp10'] == index
        assert result[index]['minavg'] == 0.5 + index

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

@freeze_time('2025-01-01')
def test_generate_current_snow_on_ground_depth():
    """
        Similar test to others that generate "current" time series
    """
    # Single day test
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id" : 5},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_snow_on_ground_depth(metrics)

    start_day = datetime.date(2024, 1, 1)
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        if(row['d'].year == 2025):
            assert row['v'] == 1
        else:
            assert row['v'] is None

    # Filter on variable ID
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id" : 5},
        {"datestamp": datetime.date(2025, 1, 1), "value": 17, "variable_id" : 1},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_snow_on_ground_depth(metrics)

    start_day = datetime.date(2024, 1, 1)
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        if(row['d'].year == 2025):
            assert row['v'] == 1
        else:
            assert row['v'] is None

    # Full year of dates
    metrics = [

    ]

    for i in range(367):
        metrics.append(
            {"datestamp": datetime.date(2024, 1, 1) + datetime.timedelta(days = i), "value": i, "variable_id" : 5}
        )

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_snow_on_ground_depth(metrics)

    start_day = datetime.date(2024, 1, 1)
    assert len(result) == 367
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        assert row['v'] == i

def test_generate_historical_snow_on_ground_depth():
    """
        Similar test to others that generate "historical" time series
    """
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 5},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_on_ground_depth(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['a'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Variable ID filter
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 5},
        {"datestamp": datetime.date(2025, 1, 2), "value": 144, "variable_id": 1},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_on_ground_depth(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['a'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Full range of quantiles on a single day
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 5, "variable_id": 5},
        {"datestamp": datetime.date(2024, 1, 1), "value": 4, "variable_id": 5},
        {"datestamp": datetime.date(2023, 1, 1), "value": 3, "variable_id": 5},
        {"datestamp": datetime.date(2022, 1, 1), "value": 2, "variable_id": 5},
        {"datestamp": datetime.date(2021, 1, 1), "value": 1, "variable_id": 5}
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_on_ground_depth(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['a'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Full range of quantiles on multiple days
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 5, "variable_id": 5},
        {"datestamp": datetime.date(2024, 1, 1), "value": 4, "variable_id": 5},
        {"datestamp": datetime.date(2023, 1, 1), "value": 3, "variable_id": 5},
        {"datestamp": datetime.date(2022, 1, 1), "value": 2, "variable_id": 5},
        {"datestamp": datetime.date(2021, 1, 1), "value": 1, "variable_id": 5},
        {"datestamp": datetime.date(2025, 1, 2), "value": 5, "variable_id": 5},
        {"datestamp": datetime.date(2024, 1, 2), "value": 4, "variable_id": 5},
        {"datestamp": datetime.date(2023, 1, 2), "value": 3, "variable_id": 5},
        {"datestamp": datetime.date(2022, 1, 2), "value": 2, "variable_id": 5},
        {"datestamp": datetime.date(2021, 1, 2), "value": 1, "variable_id": 5},
        {"datestamp": datetime.date(2025, 1, 3), "value": 5, "variable_id": 5},
        {"datestamp": datetime.date(2024, 1, 3), "value": 4, "variable_id": 5},
        {"datestamp": datetime.date(2023, 1, 3), "value": 3, "variable_id": 5},
        {"datestamp": datetime.date(2022, 1, 3), "value": 2, "variable_id": 5},
        {"datestamp": datetime.date(2021, 1, 3), "value": 1, "variable_id": 5},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_on_ground_depth(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['a'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['p10'] == 1.0

    second_day_of_year = results[1]
    assert second_day_of_year['d'] == 2
    assert second_day_of_year['p90'] == 5.0
    assert second_day_of_year['p75'] == 4.0
    assert second_day_of_year['a'] == 3.0
    assert second_day_of_year['p25'] == 2.0
    assert second_day_of_year['p10'] == 1.0

    third_day_of_year = results[2]
    assert third_day_of_year['d'] == 3
    assert third_day_of_year['p90'] == 5.0
    assert third_day_of_year['p75'] == 4.0
    assert third_day_of_year['a'] == 3.0
    assert third_day_of_year['p25'] == 2.0
    assert third_day_of_year['p10'] == 1.0

    index = 4
    for day in results[3:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

@freeze_time('2025-01-01')
def test_generate_current_snow_water_equivalent():
    """
        Similar test to others that generate "current" time series
    """
    # Single day test
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id" : 16},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_snow_water_equivalent(metrics)

    start_day = datetime.date(2024, 1, 1)
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        if(row['d'].year == 2025):
            assert row['v'] == 1
        else:
            assert row['v'] is None

    # Filter on variable ID
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id" : 16},
        {"datestamp": datetime.date(2025, 1, 1), "value": 17, "variable_id" : 1},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_snow_water_equivalent(metrics)

    start_day = datetime.date(2024, 1, 1)
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        if(row['d'].year == 2025):
            assert row['v'] == 1
        else:
            assert row['v'] is None

    # Full year of dates
    metrics = []

    for i in range(367):
        metrics.append(
            {"datestamp": datetime.date(2024, 1, 1) + datetime.timedelta(days = i), "value": i, "variable_id" : 16}
        )

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_snow_water_equivalent(metrics)

    start_day = datetime.date(2024, 1, 1)
    assert len(result) == 367
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        assert row['v'] == i

def test_generate_historical_snow_water_equivalent():
    """
        Similar test to others that generate "historical" time series
    """
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 16},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_water_equivalent(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['a'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Variable ID filter
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 16},
        {"datestamp": datetime.date(2025, 1, 2), "value": 144, "variable_id": 1},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_water_equivalent(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['a'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Full range of quantiles on a single day
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 5, "variable_id": 16},
        {"datestamp": datetime.date(2024, 1, 1), "value": 4, "variable_id": 16},
        {"datestamp": datetime.date(2023, 1, 1), "value": 3, "variable_id": 16},
        {"datestamp": datetime.date(2022, 1, 1), "value": 2, "variable_id": 16},
        {"datestamp": datetime.date(2021, 1, 1), "value": 1, "variable_id": 16}
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_water_equivalent(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['a'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Full range of quantiles on multiple days
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 5, "variable_id": 16},
        {"datestamp": datetime.date(2024, 1, 1), "value": 4, "variable_id": 16},
        {"datestamp": datetime.date(2023, 1, 1), "value": 3, "variable_id": 16},
        {"datestamp": datetime.date(2022, 1, 1), "value": 2, "variable_id": 16},
        {"datestamp": datetime.date(2021, 1, 1), "value": 1, "variable_id": 16},
        {"datestamp": datetime.date(2025, 1, 2), "value": 5, "variable_id": 16},
        {"datestamp": datetime.date(2024, 1, 2), "value": 4, "variable_id": 16},
        {"datestamp": datetime.date(2023, 1, 2), "value": 3, "variable_id": 16},
        {"datestamp": datetime.date(2022, 1, 2), "value": 2, "variable_id": 16},
        {"datestamp": datetime.date(2021, 1, 2), "value": 1, "variable_id": 16},
        {"datestamp": datetime.date(2025, 1, 3), "value": 5, "variable_id": 16},
        {"datestamp": datetime.date(2024, 1, 3), "value": 4, "variable_id": 16},
        {"datestamp": datetime.date(2023, 1, 3), "value": 3, "variable_id": 16},
        {"datestamp": datetime.date(2022, 1, 3), "value": 2, "variable_id": 16},
        {"datestamp": datetime.date(2021, 1, 3), "value": 1, "variable_id": 16},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_snow_water_equivalent(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['a'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['p10'] == 1.0

    second_day_of_year = results[1]
    assert second_day_of_year['d'] == 2
    assert second_day_of_year['p90'] == 5.0
    assert second_day_of_year['p75'] == 4.0
    assert second_day_of_year['a'] == 3.0
    assert second_day_of_year['p25'] == 2.0
    assert second_day_of_year['p10'] == 1.0

    third_day_of_year = results[2]
    assert third_day_of_year['d'] == 3
    assert third_day_of_year['p90'] == 5.0
    assert third_day_of_year['p75'] == 4.0
    assert third_day_of_year['a'] == 3.0
    assert third_day_of_year['p25'] == 2.0
    assert third_day_of_year['p10'] == 1.0

    index = 4
    for day in results[3:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

@freeze_time("2025-01-01")
def test_generate_current_manual_snow_survey():
    """
        Similar test to others that generate "current" time series
    """
    # Single day test
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id" : 19, "survey_period": "Thu, 01 May 2025 00:00:00 GMT"},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_manual_snow_survey(metrics)

    start_day = datetime.date(2024, 1, 1)
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        if(row['d'].year == 2025):
            assert row['v'] == 1
            assert row['survey_period'] == "Thu, 01 May 2025 00:00:00 GMT"
        else:
            assert row['v'] is None
            assert row['survey_period'] is None

    # Test sorting on survey_period
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id" : 19, "survey_period": "Thu, 01 May 2025 00:00:00 GMT"},
        {"datestamp": datetime.date(2025, 1, 1), "value": 10, "variable_id" : 19, "survey_period": "a"}
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_manual_snow_survey(metrics)

    start_day = datetime.date(2024, 1, 1)
    for i in range(len(result)):
        row = result[i]
        if(row['survey_period'] == 'a'):
            assert row['v'] == 10
            assert row['d'] == start_day + datetime.timedelta(days = 366)
        else:
            assert row['d'] == start_day + datetime.timedelta(days = i)
            if(row['d'].year == 2025):
                assert row['v'] == 1
                assert row['survey_period'] == "Thu, 01 May 2025 00:00:00 GMT"
            else:
                assert row['v'] is None
                assert row['survey_period'] is None


    # Filter on variable ID
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id" : 19, "survey_period": "Thu, 01 May 2025 00:00:00 GMT"},
        {"datestamp": datetime.date(2025, 1, 1), "value": 17, "variable_id" : 1,  "survey_period": "Thu, 01 May 2025 00:00:00 GMT"},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_manual_snow_survey(metrics)

    start_day = datetime.date(2024, 1, 1)
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        if(row['d'].year == 2025):
            assert row['v'] == 1
        else:
            assert row['v'] is None

    # Full year of dates
    metrics = []

    for i in range(367):
        metrics.append(
            {"datestamp": datetime.date(2024, 1, 1) + datetime.timedelta(days = i), "value": i, "variable_id" : 19, "survey_period": "Thu, 01 May 2025 00:00:00 GMT"}
        )

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_manual_snow_survey(metrics)

    start_day = datetime.date(2024, 1, 1)
    assert len(result) == 367
    for i in range(len(result)):
        row = result[i]
        assert row['d'] == start_day + datetime.timedelta(days = i)
        assert row['v'] == i

def test_generate_historical_manual_snow_survey():
    """
        Similar test to others that generate "historical" time series
    """
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 19},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_manual_snow_survey(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Variable ID filter
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 1, "variable_id": 19},
        {"datestamp": datetime.date(2025, 1, 2), "value": 144, "variable_id": 1},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_manual_snow_survey(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Full range of quantiles on a single day
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 5, "variable_id": 19},
        {"datestamp": datetime.date(2024, 1, 1), "value": 4, "variable_id": 19},
        {"datestamp": datetime.date(2023, 1, 1), "value": 3, "variable_id": 19},
        {"datestamp": datetime.date(2022, 1, 1), "value": 2, "variable_id": 19},
        {"datestamp": datetime.date(2021, 1, 1), "value": 1, "variable_id": 19}
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_manual_snow_survey(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['p50'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['p10'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

    # Full range of quantiles on multiple days
    metrics = [
        {"datestamp": datetime.date(2025, 1, 1), "value": 5, "variable_id": 19},
        {"datestamp": datetime.date(2024, 1, 1), "value": 4, "variable_id": 19},
        {"datestamp": datetime.date(2023, 1, 1), "value": 3, "variable_id": 19},
        {"datestamp": datetime.date(2022, 1, 1), "value": 2, "variable_id": 19},
        {"datestamp": datetime.date(2021, 1, 1), "value": 1, "variable_id": 19},
        {"datestamp": datetime.date(2025, 1, 2), "value": 5, "variable_id": 19},
        {"datestamp": datetime.date(2024, 1, 2), "value": 4, "variable_id": 19},
        {"datestamp": datetime.date(2023, 1, 2), "value": 3, "variable_id": 19},
        {"datestamp": datetime.date(2022, 1, 2), "value": 2, "variable_id": 19},
        {"datestamp": datetime.date(2021, 1, 2), "value": 1, "variable_id": 19},
        {"datestamp": datetime.date(2025, 1, 3), "value": 5, "variable_id": 19},
        {"datestamp": datetime.date(2024, 1, 3), "value": 4, "variable_id": 19},
        {"datestamp": datetime.date(2023, 1, 3), "value": 3, "variable_id": 19},
        {"datestamp": datetime.date(2022, 1, 3), "value": 2, "variable_id": 19},
        {"datestamp": datetime.date(2021, 1, 3), "value": 1, "variable_id": 19},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_historical_manual_snow_survey(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['p90'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['p50'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['p10'] == 1.0

    second_day_of_year = results[1]
    assert second_day_of_year['d'] == 2
    assert second_day_of_year['p90'] == 5.0
    assert second_day_of_year['p75'] == 4.0
    assert second_day_of_year['p50'] == 3.0
    assert second_day_of_year['p25'] == 2.0
    assert second_day_of_year['p10'] == 1.0

    third_day_of_year = results[2]
    assert third_day_of_year['d'] == 3
    assert third_day_of_year['p90'] == 5.0
    assert third_day_of_year['p75'] == 4.0
    assert third_day_of_year['p50'] == 3.0
    assert third_day_of_year['p25'] == 2.0
    assert third_day_of_year['p10'] == 1.0

    index = 4
    for day in results[3:]:
        assert day['d'] == index
        assert day['p90'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['p10'] is None
        index += 1

def test_generate_temperature_yearly_metrics():

    metrics = [
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 8, "value": -5, "survey_period": None},
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 1), "variable_id": 6, "value": 5, "survey_period": None},
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 8, "value": -6, "survey_period": None},
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 2), "variable_id": 6, "value": 6, "survey_period": None},
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 8, "value": -7, "survey_period": None},
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 3), "variable_id": 6, "value": 7, "survey_period": None},
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 8, "value": -8, "survey_period": None},
        {"station_id": 1, "datestamp": datetime.date(2020, 1, 4), "variable_id": 6, "value": 8, "survey_period": None}
    ]

    processed_metrics = generate_temperature_yearly_metrics(metrics, variable_ids=[6,8], year=2020)
    assert processed_metrics[0]['d'] == 1
    assert processed_metrics[0]['min'] == -5
    assert processed_metrics[0]['max'] == 5

    assert processed_metrics[1]['d'] == 2
    assert processed_metrics[1]['min'] == -6
    assert processed_metrics[1]['max'] == 6

    assert processed_metrics[2]['d'] == 3
    assert processed_metrics[2]['min'] == -7
    assert processed_metrics[2]['max'] == 7

    assert processed_metrics[3]['d'] == 4
    assert processed_metrics[3]['min'] == -8
    assert processed_metrics[3]['max'] == 8

    for i in range (4, 365):
        assert processed_metrics[i]['d'] == i + 1
        assert processed_metrics[i]['min'] == None
        processed_metrics[i]['max'] == None
