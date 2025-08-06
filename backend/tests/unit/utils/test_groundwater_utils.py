from datetime import datetime
from utils.groundwater import generate_chemistry, generate_monthly_mean_flow_by_term
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

def test_generate_chemistry():
    """
        Generate the "chemistry" statistics for different physical readings on streams.
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
