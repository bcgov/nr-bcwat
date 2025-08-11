from datetime import datetime, timedelta
from utils.streamflow import (
    generate_flow_duration_tool_metrics,
    generate_mean_annual_flow,
    generate_monthly_mean_flow_by_term,
    generate_monthly_mean_flow_by_year,
    generate_seven_day_flow_current,
    generate_seven_day_flow_historical,
    generate_stage_current,
    generate_stage_historical,
    generate_streamflow_station_metrics,
    generate_flow_metrics
)


import polars as pl
from freezegun import freeze_time

@freeze_time('2025-01-01')
def test_generate_seven_day_flow_current():
    """
        Test generating the seven day flow, simple filtering function
    """
    # Small test, generates all value 1
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-04 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-05 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-06 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-07 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1}
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


    results = generate_seven_day_flow_current(metrics)

    index = 0
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for result in results:
        assert result['d'] == start_date + timedelta(days = index)
        if(result['d'].year == 2024):
            assert result['v'] is None
        else:
            assert result['v'] == 1
        index += 1

    # Ensure variable id != 1 doesn't cause any issues
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-04 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-05 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-06 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-07 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-04 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-05 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-06 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-07 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2}
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


    results = generate_seven_day_flow_current(metrics)

    index = 0
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for result in results:
        assert result['d'] == start_date + timedelta(days = index)
        if(result['d'].year == 2024):
            assert result['v'] is None
        else:
            assert result['v'] == 1
        index += 1

@freeze_time('2025-01-01')
def test_generate_seven_day_flow_historical():
    """
        Similar to the above, but relies on generating historical quantiles for the data set
    """
    # Single day, single quantile
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
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

    results = generate_seven_day_flow_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

    #  Variable 1 filter check
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 2},
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

    results = generate_seven_day_flow_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1


    # Full range of quantiles on a single day
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 1},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 1},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1}
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

    results = generate_seven_day_flow_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['p50'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1


    # Full range of quantiles on multiple days
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 1},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 1},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 1},
        {"datestamp": datetime.strptime("2023-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2022-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 1},
        {"datestamp": datetime.strptime("2021-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 1},
        {"datestamp": datetime.strptime("2023-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2022-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 1},
        {"datestamp": datetime.strptime("2021-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
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

    results = generate_seven_day_flow_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['p50'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['min'] == 1.0

    second_day_of_year = results[1]
    assert second_day_of_year['d'] == 2
    assert second_day_of_year['max'] == 5.0
    assert second_day_of_year['p75'] == 4.0
    assert second_day_of_year['p50'] == 3.0
    assert second_day_of_year['p25'] == 2.0
    assert second_day_of_year['min'] == 1.0

    third_day_of_year = results[2]
    assert third_day_of_year['d'] == 3
    assert third_day_of_year['max'] == 5.0
    assert third_day_of_year['p75'] == 4.0
    assert third_day_of_year['p50'] == 3.0
    assert third_day_of_year['p25'] == 2.0
    assert third_day_of_year['min'] == 1.0

    index = 4
    for day in results[3:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

def test_generate_monthly_mean_flow_by_year():
    """
        Averages values for every month of the year for each given year
    """
    # Single month from single year
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
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

    # Variable id 2 test
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
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
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
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
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-03-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-04-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-05-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-06-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-07-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-08-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-09-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-10-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-11-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-12-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
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
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-03-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-04-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-05-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-06-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-07-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-08-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-09-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-10-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-11-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-12-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-02-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-02-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-03-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-03-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-04-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-04-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-05-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-05-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-06-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-06-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-07-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-07-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-08-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-08-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-09-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-09-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-10-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-10-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-11-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-11-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-12-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-12-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 1},
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
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.5, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.5, "variable_id": 1},
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


    # Ensure Variable filter works
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.5, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.5, "variable_id": 2},
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
        assert term['Jan'] == 0.5
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
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.5, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.5, "variable_id": 1},
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
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.25, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 0.75, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.25, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.75, "variable_id": 1},
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

def test_generate_mean_annual_flow():
    """
        Test generating the mean annual flow given different data sets
    """
    # Empty inputs - no values with the correct variable_id
    metrics = [
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1.5, "variable_id": 2},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
        }
    )

    result = generate_mean_annual_flow(metrics)
    assert result == None

    # Have less than 10 years, data should be the mean of all numbers
    # To test this, ensure that the data would be different if it was mean of year
    # Have unbalanced, more values in one year than another - should be closer to year with more values
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 1},
    ]

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
        }
    )

    result = generate_mean_annual_flow(metrics)
    assert result == 2.0

    # Have less than 10 FULL years, data should be the mean of all numbers
    # To test this, ensure that the data would be different if it was mean of year
    # Have unbalanced, more values in one year than another - should be closer to year with more values
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 8, "variable_id": 1},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 20, "variable_id": 1},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2019-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2017-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2016-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2015-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 20, "variable_id": 1},
    ]
    # Expected value -> 10 (sum is 120 / 12 data points), would be different (119/11) if logic is wrong

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
        }
    )

    result = generate_mean_annual_flow(metrics)
    assert result == 10.0

    # Have less than 10 FULL years, data should be the mean of all numbers
    # To test this, have our old data and then 10 full years of data
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 8, "variable_id": 1},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 20, "variable_id": 1},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2019-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2017-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2016-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2015-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 20, "variable_id": 1},
    ]
    # Add 10 years of full data in the 60s - all of the above should be ignored
    start_date = datetime.strptime("1960-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for i in range(10):
        if(start_date.year % 4 == 0):
            for j in range(366):
                metrics.append(
                    {"datestamp": start_date + timedelta(days = j), "value": 1, "variable_id": 1},
                )
            start_date += timedelta(days = 366)
        else:
            for j in range(365):
                metrics.append(
                    {"datestamp": start_date + timedelta(days = j), "value": 1, "variable_id": 1},
                )
            start_date += timedelta(days = 365)

    # Expected value -> 1 as the other values should not be used


    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
        }
    )

    result = generate_mean_annual_flow(metrics)
    assert result == 1.0


    # Have less than 10 FULL years, data should be the mean of all numbers
    # To test this, have our old data and then 10 full years of data
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 8, "variable_id": 1},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 20, "variable_id": 1},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2019-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2018-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2017-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2016-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 10, "variable_id": 1},
        {"datestamp": datetime.strptime("2015-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 20, "variable_id": 1},
    ]
    # Add 10 years of full data in the 60s - all of the above should be ignored
    start_date = datetime.strptime("1960-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for i in range(10):
        if(start_date.year % 4 == 0):
            for j in range(366):
                metrics.append(
                    {"datestamp": start_date + timedelta(days = j), "value": i, "variable_id": 1},
                )
            start_date += timedelta(days = 366)
        else:
            for j in range(365):
                metrics.append(
                    {"datestamp": start_date + timedelta(days = j), "value": i, "variable_id": 1},
                )
            start_date += timedelta(days = 365)

    # Expected value -> 1+2+3+4+5+6+7+8+9 / 10 => 45/10 = 4.5

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
        }
    )

    result = generate_mean_annual_flow(metrics)
    assert result == 4.5

@freeze_time('2025-01-01')
def test_generate_stage_current():
    """
    Very similar logic to generate_seven_day_flow_current but with a different variable id (2)
    """
    # Small test, generates all value 1 for each month
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-04 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-05 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-06 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-07 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2}
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


    results = generate_stage_current(metrics)

    index = 0
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for result in results:
        assert result['d'] == start_date + timedelta(days = index)
        if(result['d'].year == 2024):
            assert result['v'] is None
        else:
            assert result['v'] == 1
        index += 1

    # Ensure variable id != 1 doesn't cause any issues
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-04 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-05 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-06 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-07 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-04 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-05 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-06 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2024-01-07 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1}
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


    results = generate_stage_current(metrics)

    index = 0
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for result in results:
        assert result['d'] == start_date + timedelta(days = index)
        if(result['d'].year == 2024):
            assert result['v'] is None
        else:
            assert result['v'] == 1
        index += 1

@freeze_time('2025-01-01')
def test_generate_stage_historical():
    """
        Similar to the above, but relies on generating historical quantiles for the data set
    """
    # Single day, single quantile
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
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

    results = generate_stage_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

    #  Variable 1 filter check
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
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

    results = generate_stage_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1


    # Full range of quantiles on a single day
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 2},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 2},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 2},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2}
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

    results = generate_stage_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['p50'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in results[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1


    # Full range of quantiles on multiple days
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 2},
        {"datestamp": datetime.strptime("2023-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 2},
        {"datestamp": datetime.strptime("2022-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 2},
        {"datestamp": datetime.strptime("2021-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 2},
        {"datestamp": datetime.strptime("2023-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 2},
        {"datestamp": datetime.strptime("2022-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 2},
        {"datestamp": datetime.strptime("2021-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
        {"datestamp": datetime.strptime("2025-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 5, "variable_id": 2},
        {"datestamp": datetime.strptime("2024-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 4, "variable_id": 2},
        {"datestamp": datetime.strptime("2023-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 3, "variable_id": 2},
        {"datestamp": datetime.strptime("2022-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 2, "variable_id": 2},
        {"datestamp": datetime.strptime("2021-01-03 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
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

    results = generate_stage_historical(metrics)

    first_day_of_year = results[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 5.0
    assert first_day_of_year['p75'] == 4.0
    assert first_day_of_year['p50'] == 3.0
    assert first_day_of_year['p25'] == 2.0
    assert first_day_of_year['min'] == 1.0

    second_day_of_year = results[1]
    assert second_day_of_year['d'] == 2
    assert second_day_of_year['max'] == 5.0
    assert second_day_of_year['p75'] == 4.0
    assert second_day_of_year['p50'] == 3.0
    assert second_day_of_year['p25'] == 2.0
    assert second_day_of_year['min'] == 1.0

    third_day_of_year = results[2]
    assert third_day_of_year['d'] == 3
    assert third_day_of_year['max'] == 5.0
    assert third_day_of_year['p75'] == 4.0
    assert third_day_of_year['p50'] == 3.0
    assert third_day_of_year['p25'] == 2.0
    assert third_day_of_year['min'] == 1.0

    index = 4
    for day in results[3:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

def test_generate_flow_duration_tool_metrics():
    """
        Generate the flow duration tool metrics, simple formatting function
    """
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
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

    results = generate_flow_duration_tool_metrics(metrics)

    first_result = results[0]
    assert first_result['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    assert first_result['v'] == 1
    assert first_result['y'] == 2025
    assert first_result['m'] == 1

    # Filter out variable id 2
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-02 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
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

    results = generate_flow_duration_tool_metrics(metrics)

    assert len(results) == 1
    first_result = results[0]
    assert first_result['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    assert first_result['v'] == 1
    assert first_result['y'] == 2025
    assert first_result['m'] == 1

    # Entire year of data test
    index = 0
    start_date = datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    metrics = []
    while index < 365:
        metrics.append(
            {"datestamp": start_date + timedelta(days = index), "value": index, "variable_id": 1},
        )
        index += 1

    metrics = pl.LazyFrame(
        metrics,
        schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
    })

    results = generate_flow_duration_tool_metrics(metrics)

    assert len(results) == 365
    index = 0
    for result in results:
        assert result['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date() + timedelta(days = index)
        assert result['v'] == index
        assert result['y'] == 2025
        assert result['m'] == (datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date() + timedelta(days = index)).month

        index += 1

@freeze_time('2025-01-01')
def test_generate_streamflow_station_metrics():
    """
        Full E2E test of execution of all of the above functions being tested
    """
    # Single values
    metrics = [
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 1},
        {"datestamp": datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date(), "value": 1, "variable_id": 2},
    ]

    result = generate_streamflow_station_metrics(metrics)

    seven_day_flow_current = result['sevenDayFlow']['current']
    index = 0
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for val in seven_day_flow_current:
        assert val['d'] == start_date + timedelta(days = index)
        if(val['d'].year == 2024):
            assert val['v'] is None
        else:
            assert val['v'] == 1
        index += 1

    seven_day_flow_historical = result['sevenDayFlow']['historical']
    first_day_of_year = seven_day_flow_historical[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    index = 2
    for day in seven_day_flow_historical[1:]:
        assert day['d'] == index
        assert day['max'] is None
        assert day['p75'] is None
        assert day['p50'] is None
        assert day['p25'] is None
        assert day['min'] is None
        index += 1

    monthly_mean_flow_year = result['monthlyMeanFlow']['years']

    single_year = monthly_mean_flow_year[0]
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

    monthly_mean_flow_term = result['monthlyMeanFlow']['terms']

    for term in monthly_mean_flow_term:
        assert term['term'] is not None
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

    stage_current = result['stage']["current"]

    index = 0
    start_date = datetime.strptime("2024-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    for val in stage_current:
        assert val['d'] == start_date + timedelta(days = index)
        if(val['d'].year == 2024):
            assert val['v'] is None
        else:
            assert val['v'] == 1
        index += 1

    stage_historical = result['stage']['historical']

    first_day_of_year = stage_historical[0]
    assert first_day_of_year['d'] == 1
    assert first_day_of_year['max'] == 1.0
    assert first_day_of_year['p75'] == 1.0
    assert first_day_of_year['p50'] == 1.0
    assert first_day_of_year['p25'] == 1.0
    assert first_day_of_year['min'] == 1.0

    flow_duration_tool = result['flowDurationTool']

    first_result = flow_duration_tool[0]
    assert first_result['d'] == datetime.strptime("2025-01-01 00:00:00", "%Y-%m-%d %H:%M:%S").date()
    assert first_result['v'] == 1
    assert first_result['y'] == 2025
    assert first_result['m'] == 1

    mean_annual_flow = result['meanAnnualFlow']

    assert mean_annual_flow == 1

    # Do another E2E test with some fixture data
    from fixtures.streamflow.station_42648_metrics import station_metrics

    result = generate_streamflow_station_metrics(station_metrics)

    from fixtures.streamflow.station_42648_generated_metrics import expected_result

    assert result['flowDurationTool'] == expected_result['flowDurationTool']
    assert round(result['meanAnnualFlow'], 5) == round(expected_result['meanAnnualFlow'], 5)
    index = 0
    for val in result['monthlyMeanFlow']['terms']:
        for k in val.keys():
            if(k != 'term'):
                assert round(val[k], 5) == round(expected_result['monthlyMeanFlow']['terms'][index][k], 5)
            else:
                assert val[k] == expected_result['monthlyMeanFlow']['terms'][index][k]
        index += 1

def test_generate_flow_metrics():
    """
        Reformats an input
    """
    flow_metrics = {
        "station_flow_metric" : {
            "ipf_1": 1,
            "ipf_2": 2,
            "ipf_5": 3,
            "ipf_10": 4,
            "ipf_20": 5,
            "ipf_25": 6,
            "ipf_50": 7,
            "ipf_100": 8,
            "ipf_200": 9,
            "ipf_1_01": 10,
            "ipf_yr": [1970],
            "amfh_1": 11,
            "amfh_2": 12,
            "amfh_5": 13,
            "amfh_10": 14,
            "amfh_20": 15,
            "amfh_25": 16,
            "amfh_50": 17,
            "amfh_100":18,
            "amfh_200":19,
            "amfh_1_01": 20,
            "amfh_yr": [1971],
            "amfl_1": 21,
            "amfl_2": 22,
            "amfl_5": 23,
            "amfl_10": 24,
            "amfl_20": 25,
            "amfl_25": 26,
            "amfl_50": 27,
            "amfl_100":28,
            "amfl_200":29,
            "amfl_1_01": 30,
            "amfl_yr": [1972],
            "js_7df_1": 31,
            "js_7df_2": 32,
            "js_7df_5": 33,
            "js_7df_10": 34,
            "js_7df_20": 35,
            "js_7df_25": 36,
            "js_7df_50": 37,
            "js_7df_100":38,
            "js_7df_200":39,
            "js_7df_1_01": 40,
            "js_7df_yr": [1973],
            "ann_7df_1": 41,
            "ann_7df_2": 42,
            "ann_7df_5": 43,
            "ann_7df_10": 44,
            "ann_7df_20": 45,
            "ann_7df_25": 46,
            "ann_7df_50": 47,
            "ann_7df_100":48,
            "ann_7df_200":49,
            "ann_7df_1_01": 50,
            "ann_7df_yr": [1974],
        }
    }

    result = generate_flow_metrics(flow_metrics)
    instantaneous = result[0]
    assert instantaneous["1"] == 1
    assert instantaneous["2"] == 2
    assert instantaneous["5"] == 3
    assert instantaneous["10"] == 4
    assert instantaneous["20"] == 5
    assert instantaneous["25"] == 6
    assert instantaneous["50"] == 7
    assert instantaneous["100"] == 8
    assert instantaneous["200"] == 9
    assert instantaneous["1.01"] == 10
    assert instantaneous["Years of data"] == [1970]
    assert instantaneous["Parameter"] == "Instantaneous Peak Flow (m3/s)"

    annual_mean = result[1]
    assert annual_mean["1"] == 11
    assert annual_mean["2"] == 12
    assert annual_mean["5"] == 13
    assert annual_mean["10"] == 14
    assert annual_mean["20"] == 15
    assert annual_mean["25"] == 16
    assert annual_mean["50"] == 17
    assert annual_mean["100"] == 18
    assert annual_mean["200"] == 19
    assert annual_mean["1.01"] == 20
    assert annual_mean["Years of data"] == [1971]
    assert annual_mean["Parameter"] == "Annual Mean Flow (high, m3/s)"

    annual_mean_low = result[2]
    assert annual_mean_low["1"] == 21
    assert annual_mean_low["2"] == 22
    assert annual_mean_low["5"] == 23
    assert annual_mean_low["10"] == 24
    assert annual_mean_low["20"] == 25
    assert annual_mean_low["25"] == 26
    assert annual_mean_low["50"] == 27
    assert annual_mean_low["100"] == 28
    assert annual_mean_low["200"] == 29
    assert annual_mean_low["1.01"] == 30
    assert annual_mean_low["Years of data"] == [1972]
    assert annual_mean_low["Parameter"] == "Annual Mean Flow (low, m3/s)"

    june_sept_low = result[3]
    assert june_sept_low["1"] == 31
    assert june_sept_low["2"] == 32
    assert june_sept_low["5"] == 33
    assert june_sept_low["10"] == 34
    assert june_sept_low["20"] == 35
    assert june_sept_low["25"] == 36
    assert june_sept_low["50"] == 37
    assert june_sept_low["100"] == 38
    assert june_sept_low["200"] == 39
    assert june_sept_low["1.01"] == 40
    assert june_sept_low["Years of data"] == [1973]
    assert june_sept_low["Parameter"] == "June-Sept 7 Day Low Flow (m3/s)"

    annual_flow = result[4]
    assert annual_flow["1"] == 41
    assert annual_flow["2"] == 42
    assert annual_flow["5"] == 43
    assert annual_flow["10"] == 44
    assert annual_flow["20"] == 45
    assert annual_flow["25"] == 46
    assert annual_flow["50"] == 47
    assert annual_flow["100"] == 48
    assert annual_flow["200"] == 49
    assert annual_flow["1.01"] == 50
    assert annual_flow["Years of data"] == [1974]
    assert annual_flow["Parameter"] == "Annual 7 Day Low Flow (m3/s)"
