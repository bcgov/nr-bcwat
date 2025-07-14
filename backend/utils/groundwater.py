import polars as pl

def generate_current_hydrograph(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    ).collect().to_dicts()

def generate_historical_hydrograph(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .group_by("d")
        .agg([
            pl.col("v").max().alias("max"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("a"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").min().alias("min")
        ])
        .select("d", "max", "p75", "a", "p25", "min")
        .sort("d")
    ).collect().to_dicts()

def generate_current_monthly_mean_flow(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .with_columns(
            m=pl.col("datestamp").dt.month(),
            v=pl.col("value")
        )
        .group_by("m")
        .agg([
            pl.col("v").max().alias("max"),
            pl.col("v").mean().alias("avg"),
            pl.col("v").min().alias("min")
        ])
        .select("m", "max", "avg", "min")
        .sort("m")
    ).collect().to_dicts()

def generate_yearly_monthly_mean_flow(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .with_columns(
            year=pl.col("datestamp").dt.year(),
            m=pl.col("datestamp").dt.month(),
            v=pl.col("value")
        )
        .group_by("year", "m")
        .agg([
            pl.col("v").sum().alias("v"),
            pl.col("v").count().alias("days"),
            pl.col("v").mean().alias("avg")
        ])
        .select("year", "m",  "v", "avg", 'days')
        .sort("year", "m")
    ).collect().to_dicts()

def generate_groundwater_level_station_metrics(metrics: list[dict]) -> list[dict]:
    raw_metrics_lf = pl.LazyFrame(
            metrics,
            schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
            }
        )

    current_hydrograph = generate_current_hydrograph(raw_metrics_lf)
    historical_hydrograph = generate_historical_hydrograph(raw_metrics_lf)
    current_monthly_mean_flow = generate_current_monthly_mean_flow(raw_metrics_lf)
    yearly_monthly_mean_flow = generate_yearly_monthly_mean_flow(raw_metrics_lf)

    return {
        "hydrograph": {
            "current": current_hydrograph,
            "historical": historical_hydrograph
        },
        "monthly_mean_flow": {
            "current": current_monthly_mean_flow,
            "yearly": yearly_monthly_mean_flow
        }
    }

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
        .group_by(["paramId", "units", "title"])
        .agg([
            pl.struct(["d", "v"]).alias("data")
        ])
        .select("paramId", "units", "title", "data")
        .sort('paramId')
    ).collect().to_dicts()

def generate_groundwater_quality_station_metrics(metrics: list[dict]) -> list[dict]:

    raw_metrics_lf = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datetimestamp': pl.Datetime,
            'value': pl.Float64,
            'value_text': pl.String,
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
