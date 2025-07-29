from datetime import datetime, timedelta
from utils.streamflow import generate_mean_annual_flow, generate_monthly_mean_flow_by_term
import polars as pl

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

