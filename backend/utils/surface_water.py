import polars as pl
import json
from datetime import datetime

def generate_chemistry(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .with_columns(
            paramId=pl.col("parameter_id"),
            units=pl.col("unit_name"),
            title=pl.col("parameter_name"),
            d=pl.col("datetimestamp"),
            v=pl.col("value").alias("v"),
        )
        .sort('paramId', 'd')
        .group_by(["paramId", "units", "title"])
        .agg([
            pl.struct(["d", "v"]).alias("data")
        ])
        .select("paramId", "units", "title", "data")
    ).collect().to_dicts()

def generate_surface_water_station_metrics(metrics: list[dict]) -> list[dict]:

    raw_metrics_lf = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datetimestamp': pl.Datetime,
            'value': pl.Float64,
            'value_letter': pl.String,
            'parameter_id': pl.Int32,
            'parameter_name': pl.String,
            'grouping_id': pl.Int32,
            'grouping_name': pl.String,
            'unit_id': pl.Int32,
            'unit_name': pl.String
        }
    )

    chemistry = generate_chemistry(raw_metrics_lf)

    return chemistry
