import polars as pl

def generate_chemistry(metrics: pl.LazyFrame) -> list[dict]:
    unique_params = (
        metrics.
        select(
            pl.col("parameter_id")
        )
        .collect()
        .n_unique()
    )

    sample_dates = (
        metrics.
        select(
            pl.count("datetimestamp")
        )
        .collect()["datetimestamp"][0]
    )

    return ((
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
    ).collect().to_dicts(), unique_params, sample_dates)

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

    (chemistry, unique_params, sample_dates)  = generate_chemistry(raw_metrics_lf)

    return (chemistry, unique_params, sample_dates)
