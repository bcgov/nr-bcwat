from datetime import datetime, timedelta
from utils.groundwater import (
    generate_chemistry,
    generate_current_hydrograph,
    generate_groundwater_level_station_metrics,
    generate_historical_hydrograph,
    generate_monthly_mean_flow_by_term,
    generate_monthly_mean_flow_by_year,
    generate_groundwater_quality_station_metrics
)
import polars as pl
from freezegun import freeze_time




@freeze_time('2025-01-01')
def test_generate_current_hydrograph():
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
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

    result = generate_current_hydrograph(metrics)

    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    index = 0
    for value in result:
        assert value['d'] == start_date + timedelta(days = index)
        if(value['d'].year == 2025):
            assert value['v'] == 1
        else:
            assert value['v'] is None
        index += 1

    metrics = [
        {"datestamp": datetime.strptime("2024-12-25 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2},
        {"datestamp": datetime.strptime("2024-12-26 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-12-27 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4},
        {"datestamp": datetime.strptime("2024-12-28 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5},
        {"datestamp": datetime.strptime("2024-12-29 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 6},
        {"datestamp": datetime.strptime("2024-12-30 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 7},
        {"datestamp": datetime.strptime("2024-12-31 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 8},
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 9}
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

    result = generate_current_hydrograph(metrics)

    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    index = 0
    for value in result:
        assert value['d'] == start_date + timedelta(days = index)
        if(value['d'].year == 2025 or value['d'].month == 12 and value['d'].day > 24):
            assert value['v'] == index - 357
        else:
            assert value['v'] is None
        index += 1

    # programmatically make a test case with a full year of data
    full_year_data = []
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    index = 0
    while index < 370:
        entry =  {
                "datestamp": start_date + timedelta(days =index),
                "value": index
            }
        full_year_data.append(entry)
        index += 1

    metrics = pl.LazyFrame(
        full_year_data,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    result = generate_current_hydrograph(metrics)

    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    index = 0
    # Assure the days after the current day are filtered out
    assert len(result) == 367
    for value in result:
        assert value['d'] == start_date + timedelta(days = index)
        assert value['v'] == index
        index += 1



def test_generate_historical_hydrograph():
    """
        Generate historical hydrograph data with quantiles
    """
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
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

    results = generate_historical_hydrograph(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['a'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

        # Full range of quantiles on a single day
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1}
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

    results = generate_historical_hydrograph(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['a'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

    # Full range of quantiles on multiple days
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4},
        {"datestamp": datetime.strptime("2023-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2022-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2},
        {"datestamp": datetime.strptime("2021-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5},
        {"datestamp": datetime.strptime("2024-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4},
        {"datestamp": datetime.strptime("2023-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2022-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2},
        {"datestamp": datetime.strptime("2021-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
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

    results = generate_historical_hydrograph(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['a'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['min'] == 1.0

    second_day_of_year = results[1]
    assert second_day_of_year['d'] == 2
    assert second_day_of_year['max'] == 5.0
    assert second_day_of_year['p75'] == 4.0
    assert second_day_of_year['a'] == 3.0
    assert second_day_of_year['p25'] == 2.0
    assert second_day_of_year['min'] == 1.0

    third_day_of_year = results[2]
    assert third_day_of_year['d'] == 3
    assert third_day_of_year['max'] == 5.0
    assert third_day_of_year['p75'] == 4.0
    assert third_day_of_year['a'] == 3.0
    assert third_day_of_year['p25'] == 2.0
    assert third_day_of_year['min'] == 1.0

    index = 4
    for day in results[3:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

def test_generate_monthly_mean_flow_by_year():
    """
        Averages values for every month of the year for each given year
    """
    # Single month from single year
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
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

    results = generate_monthly_mean_flow_by_year(metrics)

    single_year = results[0]
    assert single_year['year'] == 2025
    assert single_year['Jan'] == 1.0
    assert single_year['Feb'] is None
    assert single_year['Mar'] is None
    assert single_year['Apr'] is None
    assert single_year['May'] is None
    assert single_year['Jun'] is None
    assert single_year['Jul'] is None
    assert single_year['Aug'] is None
    assert single_year['Sep'] is None
    assert single_year['Oct'] is None
    assert single_year['Nov'] is None
    assert single_year['Dec'] is None

    # Actually has to calculate average
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
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

    results = generate_monthly_mean_flow_by_year(metrics)

    single_year = results[0]
    assert single_year['year'] == 2025
    assert single_year['Jan'] == 2.0
    assert single_year['Feb'] is None
    assert single_year['Mar'] is None
    assert single_year['Apr'] is None
    assert single_year['May'] is None
    assert single_year['Jun'] is None
    assert single_year['Jul'] is None
    assert single_year['Aug'] is None
    assert single_year['Sep'] is None
    assert single_year['Oct'] is None
    assert single_year['Nov'] is None
    assert single_year['Dec'] is None

    # Actually has to calculate average for multiple months in a single year
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-03-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-04-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-05-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-06-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-07-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-08-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-09-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-10-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-11-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-12-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
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

    results = generate_monthly_mean_flow_by_year(metrics)

    single_year = results[0]
    assert single_year['year'] == 2025
    assert single_year['Jan'] == 2.0
    assert single_year['Feb'] == 2.0
    assert single_year['Mar'] == 2.0
    assert single_year['Apr'] == 2.0
    assert single_year['May'] == 2.0
    assert single_year['Jun'] == 2.0
    assert single_year['Jul'] == 2.0
    assert single_year['Aug'] == 2.0
    assert single_year['Sep'] == 2.0
    assert single_year['Oct'] == 2.0
    assert single_year['Nov'] == 2.0
    assert single_year['Dec'] == 2.0

    # Actually has to calculate average for multiple months in multiple years
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-03-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-04-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-05-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-06-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-07-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-08-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-09-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-10-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-11-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-12-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-03-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-04-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-05-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-06-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-07-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-08-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-09-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-10-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-11-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
        {"datestamp": datetime.strptime("2024-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2024-12-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3},
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

    results = generate_monthly_mean_flow_by_year(metrics)

    closest_year = results[0]
    assert closest_year['year'] == 2025
    assert closest_year['Jan'] == 2.0
    assert closest_year['Feb'] == 2.0
    assert closest_year['Mar'] == 2.0
    assert closest_year['Apr'] == 2.0
    assert closest_year['May'] == 2.0
    assert closest_year['Jun'] == 2.0
    assert closest_year['Jul'] == 2.0
    assert closest_year['Aug'] == 2.0
    assert closest_year['Sep'] == 2.0
    assert closest_year['Oct'] == 2.0
    assert closest_year['Nov'] == 2.0
    assert closest_year['Dec'] == 2.0

    # 2024
    second_closest_year = results[1]
    assert second_closest_year['year'] == 2024
    assert second_closest_year['Jan'] == 2.0
    assert second_closest_year['Feb'] == 2.0
    assert second_closest_year['Mar'] == 2.0
    assert second_closest_year['Apr'] == 2.0
    assert second_closest_year['May'] == 2.0
    assert second_closest_year['Jun'] == 2.0
    assert second_closest_year['Jul'] == 2.0
    assert second_closest_year['Aug'] == 2.0
    assert second_closest_year['Sep'] == 2.0
    assert second_closest_year['Oct'] == 2.0
    assert second_closest_year['Nov'] == 2.0
    assert second_closest_year['Dec'] == 2.0


def test_generate_monthly_mean_flow_by_term():
    """
        Test Generating the min/max/mean of the means of each month of the given dataset.
    """
    # Small test, generates all value 1 for each month
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1}
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

    result = generate_monthly_mean_flow_by_term(metrics)
    for term in result:
        assert term['term'] is not None
        assert term['Jan'] == 1.0
        assert term['Feb'] == 1.0
        assert term['Mar'] == 1.0
        assert term['Apr'] == 1.0
        assert term['May'] == 1.0
        assert term['Jun'] == 1.0
        assert term['Jul'] == 1.0
        assert term['Aug'] == 1.0
        assert term['Sep'] == 1.0
        assert term['Oct'] == 1.0
        assert term['Nov'] == 1.0
        assert term['Dec'] == 1.0

    # Ensure January's value is the average, not min/max of its values
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.5},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.5},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1}
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

    result = generate_monthly_mean_flow_by_term(metrics)
    for term in result:
        assert term['term'] is not None
        assert term['Jan'] == 1.0
        assert term['Feb'] == 1.0
        assert term['Mar'] == 1.0
        assert term['Apr'] == 1.0
        assert term['May'] == 1.0
        assert term['Jun'] == 1.0
        assert term['Jul'] == 1.0
        assert term['Aug'] == 1.0
        assert term['Sep'] == 1.0
        assert term['Oct'] == 1.0
        assert term['Nov'] == 1.0
        assert term['Dec'] == 1.0

    # Take different years to ensure mean/min/max are generated successfully from means of multiple years
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.5},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.5},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1}
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

    result = generate_monthly_mean_flow_by_term(metrics)
    for term in result:
        assert term['term'] is not None
        if(term['term'] == 'min'):
            assert term['Jan'] == 0.5
        elif(term['term'] == 'mean'):
            assert term['Jan'] == 1.0
        elif(term['term'] == 'max'):
            assert term['Jan'] == 1.5
        assert term['Feb'] == 1.0
        assert term['Mar'] == 1.0
        assert term['Apr'] == 1.0
        assert term['May'] == 1.0
        assert term['Jun'] == 1.0
        assert term['Jul'] == 1.0
        assert term['Aug'] == 1.0
        assert term['Sep'] == 1.0
        assert term['Oct'] == 1.0
        assert term['Nov'] == 1.0
        assert term['Dec'] == 1.0

    # Same as above, but force yearly means to be calculated
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.25},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.75},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.25},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.75},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1}
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

    result = generate_monthly_mean_flow_by_term(metrics)
    for term in result:
        assert term['term'] is not None
        if(term['term'] == 'min'):
            assert term['Jan'] == 0.5
        elif(term['term'] == 'mean'):
            assert term['Jan'] == 1.0
        elif(term['term'] == 'max'):
            assert term['Jan'] == 1.5
        assert term['Feb'] == 1.0
        assert term['Mar'] == 1.0
        assert term['Apr'] == 1.0
        assert term['May'] == 1.0
        assert term['Jun'] == 1.0
        assert term['Jul'] == 1.0
        assert term['Aug'] == 1.0
        assert term['Sep'] == 1.0
        assert term['Oct'] == 1.0
        assert term['Nov'] == 1.0
        assert term['Dec'] == 1.0

@freeze_time('2025-01-01')
def test_generate_groundwater_level_station_metrics():
    # Simple single test
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), 'value': 1},
    ]

    result = generate_groundwater_level_station_metrics(metrics)
    current_hydrograph = result['hydrograph']['current']
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    index = 0
    for value in current_hydrograph:
        assert value['d'] == start_date + timedelta(days = index)
        if(value['d'].year == 2025):
            assert value['v'] == 1
        else:
            assert value['v'] is None
        index += 1

    historical_hydrograph = result['hydrograph']['historical']
    first_day_of_year = historical_hydrograph[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['a'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in historical_hydrograph[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['a'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

    monthly_mean_flow_by_year = result['monthly_mean_flow']['years']
    single_year = monthly_mean_flow_by_year[0]
    assert single_year['year'] == 2025
    assert single_year['Jan'] == 1.0
    assert single_year['Feb'] is None
    assert single_year['Mar'] is None
    assert single_year['Apr'] is None
    assert single_year['May'] is None
    assert single_year['Jun'] is None
    assert single_year['Jul'] is None
    assert single_year['Aug'] is None
    assert single_year['Sep'] is None
    assert single_year['Oct'] is None
    assert single_year['Nov'] is None
    assert single_year['Dec'] is None

    monthly_mean_flow_by_term = result['monthly_mean_flow']['terms']
    for term in monthly_mean_flow_by_term:
        assert term['Jan'] == 1.0
        assert term['Feb'] is None
        assert term['Mar'] is None
        assert term['Apr'] is None
        assert term['May'] is None
        assert term['Jun'] is None
        assert term['Jul'] is None
        assert term['Aug'] is None
        assert term['Sep'] is None
        assert term['Oct'] is None
        assert term['Nov'] is None
        assert term['Dec'] is None

    # Full test with fixture data
    from fixtures.groundwater.station_16425_metrics import station_metrics

    data = generate_groundwater_level_station_metrics(station_metrics)

    from fixtures.groundwater.groundwater_level_station_metrics_util import expected_data

    assert data['hydrograph']['historical'] == expected_data['hydrograph']['historical']
    assert data['hydrograph']['current'] == expected_data['hydrograph']['current']
    assert data['monthly_mean_flow']['years'] == expected_data['monthly_mean_flow']['years']
    for term in data['monthly_mean_flow']['terms']:
        expected_term = next(e_term for e_term in expected_data['monthly_mean_flow']['terms'] if e_term['term'] == term['term'])
        for key in term.keys():
            if(key != 'term'):
                assert round(term[key], 5) == round(expected_term[key], 5)

def test_generate_chemistry():
    """
        Generate the "chemistry" statistics for different physical readings in groundwater.
    """
    metrics = [
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'}
    ]

    raw_metrics_lf = pl.LazyFrame(
        metrics,
        schema_overrides={
            'datetimestamp': pl.Datetime,
            'value': pl.Float64,
            'parameter_id': pl.Int32,
            'parameter_name': pl.String,
            'unit_name': pl.String
        }
    )

    (chemistry, unique_params, sample_dates)  = generate_chemistry(raw_metrics_lf)
    assert len(chemistry) == 1
    chemistry = chemistry[0]
    assert chemistry['paramId'] == 1
    assert chemistry['units'] == 'mm'
    assert chemistry['title'] == 'unit_test'
    assert chemistry['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][0]['v'] == 1
    assert unique_params == 1
    assert sample_dates == 1

    # Multiple entries for the same param
    metrics = [
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'}
    ]

    raw_metrics_lf = pl.LazyFrame(
        metrics,
        schema_overrides={
            'datetimestamp': pl.Datetime,
            'value': pl.Float64,
            'parameter_id': pl.Int32,
            'parameter_name': pl.String,
            'unit_name': pl.String
        }
    )

    (chemistry, unique_params, sample_dates)  = generate_chemistry(raw_metrics_lf)
    assert len(chemistry) == 1
    chemistry = chemistry[0]
    assert chemistry['paramId'] == 1
    assert chemistry['units'] == 'mm'
    assert chemistry['title'] == 'unit_test'
    assert len(chemistry['data']) == 2
    assert chemistry['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][0]['v'] == 1
    assert chemistry['data'][1]['d'] == datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][1]['v'] == 1
    assert unique_params == 1
    assert sample_dates == 2

    # Same date for multiple params
    metrics = [
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 2, 'parameter_name': 'unit_test_2', 'unit_name': 'mm'}
    ]

    raw_metrics_lf = pl.LazyFrame(
        metrics,
        schema_overrides={
            'datetimestamp': pl.Datetime,
            'value': pl.Float64,
            'parameter_id': pl.Int32,
            'parameter_name': pl.String,
            'unit_name': pl.String
        }
    )

    (chemistry, unique_params, sample_dates)  = generate_chemistry(raw_metrics_lf)
    assert len(chemistry) == 2
    if(chemistry[0]['paramId'] == 1):
        chemistry_1 = chemistry[1]
        chemistry = chemistry[0]
    else:
        chemistry_1 = chemistry[0]
        chemistry = chemistry[1]
    assert chemistry['paramId'] == 1
    assert chemistry['units'] == 'mm'
    assert chemistry['title'] == 'unit_test'
    assert len(chemistry['data']) == 1
    assert chemistry['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][0]['v'] == 1
    assert chemistry_1['paramId'] == 2
    assert chemistry_1['units'] == 'mm'
    assert chemistry_1['title'] == 'unit_test_2'
    assert len(chemistry_1['data']) == 1
    assert chemistry_1['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry_1['data'][0]['v'] == 1
    assert unique_params == 2
    assert sample_dates == 1


    # Multiple dates for multiple params
    metrics = [
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 2, 'parameter_name': 'unit_test_2', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 2, 'parameter_name': 'unit_test_2', 'unit_name': 'mm'}
    ]

    raw_metrics_lf = pl.LazyFrame(
        metrics,
        schema_overrides={
            'datetimestamp': pl.Datetime,
            'value': pl.Float64,
            'parameter_id': pl.Int32,
            'parameter_name': pl.String,
            'unit_name': pl.String
        }
    )

    (chemistry, unique_params, sample_dates)  = generate_chemistry(raw_metrics_lf)
    assert len(chemistry) == 2
    if(chemistry[0]['paramId'] == 1):
        chemistry_1 = chemistry[1]
        chemistry = chemistry[0]
    else:
        chemistry_1 = chemistry[0]
        chemistry = chemistry[1]
    assert chemistry['paramId'] == 1
    assert chemistry['units'] == 'mm'
    assert chemistry['title'] == 'unit_test'
    assert len(chemistry['data']) == 2
    assert chemistry['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][0]['v'] == 1
    assert chemistry['data'][1]['d'] == datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][1]['v'] == 1
    assert chemistry_1['paramId'] == 2
    assert chemistry_1['units'] == 'mm'
    assert chemistry_1['title'] == 'unit_test_2'
    assert len(chemistry_1['data']) == 2
    assert chemistry_1['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry_1['data'][0]['v'] == 1
    assert chemistry_1['data'][1]['d'] == datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry_1['data'][1]['v'] == 1
    assert unique_params == 2
    assert sample_dates == 2

def test_generate_groundwater_quality_station_metrics():
    """
        Pretty much a wrapper around the test_generate_chemistry function above, just use a couple test cases from that
    """
    metrics = [
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'}
    ]

    (chemistry, unique_params, sample_dates)  = generate_groundwater_quality_station_metrics(metrics)
    assert len(chemistry) == 1
    chemistry = chemistry[0]
    assert chemistry['paramId'] == 1
    assert chemistry['units'] == 'mm'
    assert chemistry['title'] == 'unit_test'
    assert chemistry['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][0]['v'] == 1
    assert unique_params == 1
    assert sample_dates == 1

    # Multiple dates for multiple params
    metrics = [
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 1, 'parameter_name': 'unit_test', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 2, 'parameter_name': 'unit_test_2', 'unit_name': 'mm'},
        {'datetimestamp': datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S"), 'value': 1, 'parameter_id': 2, 'parameter_name': 'unit_test_2', 'unit_name': 'mm'}
    ]

    (chemistry, unique_params, sample_dates)  = generate_groundwater_quality_station_metrics(metrics)

    assert len(chemistry) == 2
    if(chemistry[0]['paramId'] == 1):
        chemistry_1 = chemistry[1]
        chemistry = chemistry[0]
    else:
        chemistry_1 = chemistry[0]
        chemistry = chemistry[1]
    assert chemistry['paramId'] == 1
    assert chemistry['units'] == 'mm'
    assert chemistry['title'] == 'unit_test'
    assert len(chemistry['data']) == 2
    assert chemistry['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][0]['v'] == 1
    assert chemistry['data'][1]['d'] == datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry['data'][1]['v'] == 1
    assert chemistry_1['paramId'] == 2
    assert chemistry_1['units'] == 'mm'
    assert chemistry_1['title'] == 'unit_test_2'
    assert len(chemistry_1['data']) == 2
    assert chemistry_1['data'][0]['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry_1['data'][0]['v'] == 1
    assert chemistry_1['data'][1]['d'] == datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S")
    assert chemistry_1['data'][1]['v'] == 1
    assert unique_params == 2
    assert sample_dates == 2


