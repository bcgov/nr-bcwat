from datetime import datetime
from utils.surface_water import generate_chemistry
import polars as pl

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
    # same date
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
