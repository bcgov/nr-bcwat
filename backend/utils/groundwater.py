import json
import polars as pl
from utils.shared import (
    generate_current_time_series,
    generate_historical_time_series
)

def generate_current_hydrograph(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
        metrics
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    )

    return generate_current_time_series(processed_metrics=processed)

def generate_historical_hydrograph(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
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
    )

    return generate_historical_time_series(processed_metrics=processed)

def generate_monthly_mean_flow_by_year(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .with_columns(
            year=pl.col("datestamp").dt.year(),
            month=pl.col("datestamp").dt.month(),
            value=pl.col("value")
        )
        .group_by("year", "month")
        .agg([
            pl.col("value").mean().alias("value")
        ])
        .with_columns(
            year=pl.col('year'),
            Jan=pl.when(pl.col("month") == 1).then(pl.col("value")),
            Feb=pl.when(pl.col("month") == 2).then(pl.col("value")),
            Mar=pl.when(pl.col("month") == 3).then(pl.col("value")),
            Apr=pl.when(pl.col("month") == 4).then(pl.col("value")),
            May=pl.when(pl.col("month") == 5).then(pl.col("value")),
            Jun=pl.when(pl.col("month") == 6).then(pl.col("value")),
            Jul=pl.when(pl.col("month") == 7).then(pl.col("value")),
            Aug=pl.when(pl.col("month") == 8).then(pl.col("value")),
            Sep=pl.when(pl.col("month") == 9).then(pl.col("value")),
            Oct=pl.when(pl.col("month") == 10).then(pl.col("value")),
            Nov=pl.when(pl.col("month") == 11).then(pl.col("value")),
            Dec=pl.when(pl.col("month") == 12).then(pl.col("value")),
        )
        .select("year", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        .group_by("year")
        .agg([
            pl.col("Jan").max().alias("Jan"),
            pl.col("Feb").max().alias("Feb"),
            pl.col("Mar").max().alias("Mar"),
            pl.col("Apr").max().alias("Apr"),
            pl.col("May").max().alias("May"),
            pl.col("Jun").max().alias("Jun"),
            pl.col("Jul").max().alias("Jul"),
            pl.col("Aug").max().alias("Aug"),
            pl.col("Sep").max().alias("Sep"),
            pl.col("Oct").max().alias("Oct"),
            pl.col("Nov").max().alias("Nov"),
            pl.col("Dec").max().alias("Dec")
        ])
        .sort("year", descending=True)
    ).collect().to_dicts()

def generate_monthly_mean_flow_by_term(metrics: pl.LazyFrame) -> list[dict]:
    min_monthly_flow = (
        metrics
        .with_columns(
            month=pl.col("datestamp").dt.month(),
            value=pl.col("value")
        )
        .group_by("month")
        .agg([
            pl.col("value").min().alias("value")
        ])
        .with_columns(
            term=pl.lit('min'),
            Jan=pl.when(pl.col("month") == 1).then(pl.col("value")),
            Feb=pl.when(pl.col("month") == 2).then(pl.col("value")),
            Mar=pl.when(pl.col("month") == 3).then(pl.col("value")),
            Apr=pl.when(pl.col("month") == 4).then(pl.col("value")),
            May=pl.when(pl.col("month") == 5).then(pl.col("value")),
            Jun=pl.when(pl.col("month") == 6).then(pl.col("value")),
            Jul=pl.when(pl.col("month") == 7).then(pl.col("value")),
            Aug=pl.when(pl.col("month") == 8).then(pl.col("value")),
            Sep=pl.when(pl.col("month") == 9).then(pl.col("value")),
            Oct=pl.when(pl.col("month") == 10).then(pl.col("value")),
            Nov=pl.when(pl.col("month") == 11).then(pl.col("value")),
            Dec=pl.when(pl.col("month") == 12).then(pl.col("value")),
        )
        .select("term", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        .group_by("term")
        .agg([
            pl.col("Jan").max().alias("Jan"),
            pl.col("Feb").max().alias("Feb"),
            pl.col("Mar").max().alias("Mar"),
            pl.col("Apr").max().alias("Apr"),
            pl.col("May").max().alias("May"),
            pl.col("Jun").max().alias("Jun"),
            pl.col("Jul").max().alias("Jul"),
            pl.col("Aug").max().alias("Aug"),
            pl.col("Sep").max().alias("Sep"),
            pl.col("Oct").max().alias("Oct"),
            pl.col("Nov").max().alias("Nov"),
            pl.col("Dec").max().alias("Dec")
        ])
    )

    max_monthly_flow = (
        metrics
        .with_columns(
            month=pl.col("datestamp").dt.month(),
            value=pl.col("value")
        )
        .group_by("month")
        .agg([
            pl.col("value").max().alias("value")
        ])
        .with_columns(
            term=pl.lit('max'),
            Jan=pl.when(pl.col("month") == 1).then(pl.col("value")),
            Feb=pl.when(pl.col("month") == 2).then(pl.col("value")),
            Mar=pl.when(pl.col("month") == 3).then(pl.col("value")),
            Apr=pl.when(pl.col("month") == 4).then(pl.col("value")),
            May=pl.when(pl.col("month") == 5).then(pl.col("value")),
            Jun=pl.when(pl.col("month") == 6).then(pl.col("value")),
            Jul=pl.when(pl.col("month") == 7).then(pl.col("value")),
            Aug=pl.when(pl.col("month") == 8).then(pl.col("value")),
            Sep=pl.when(pl.col("month") == 9).then(pl.col("value")),
            Oct=pl.when(pl.col("month") == 10).then(pl.col("value")),
            Nov=pl.when(pl.col("month") == 11).then(pl.col("value")),
            Dec=pl.when(pl.col("month") == 12).then(pl.col("value")),
        )
        .select("term", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        .group_by("term")
        .agg([
            pl.col("Jan").max().alias("Jan"),
            pl.col("Feb").max().alias("Feb"),
            pl.col("Mar").max().alias("Mar"),
            pl.col("Apr").max().alias("Apr"),
            pl.col("May").max().alias("May"),
            pl.col("Jun").max().alias("Jun"),
            pl.col("Jul").max().alias("Jul"),
            pl.col("Aug").max().alias("Aug"),
            pl.col("Sep").max().alias("Sep"),
            pl.col("Oct").max().alias("Oct"),
            pl.col("Nov").max().alias("Nov"),
            pl.col("Dec").max().alias("Dec")
        ])
    )

    mean_monthly_flow = (
        metrics
        .with_columns(
            month=pl.col("datestamp").dt.month(),
            value=pl.col("value")
        )
        .group_by("month")
        .agg([
            pl.col("value").mean().alias("value")
        ])
        .with_columns(
            term=pl.lit('mean'),
            Jan=pl.when(pl.col("month") == 1).then(pl.col("value")),
            Feb=pl.when(pl.col("month") == 2).then(pl.col("value")),
            Mar=pl.when(pl.col("month") == 3).then(pl.col("value")),
            Apr=pl.when(pl.col("month") == 4).then(pl.col("value")),
            May=pl.when(pl.col("month") == 5).then(pl.col("value")),
            Jun=pl.when(pl.col("month") == 6).then(pl.col("value")),
            Jul=pl.when(pl.col("month") == 7).then(pl.col("value")),
            Aug=pl.when(pl.col("month") == 8).then(pl.col("value")),
            Sep=pl.when(pl.col("month") == 9).then(pl.col("value")),
            Oct=pl.when(pl.col("month") == 10).then(pl.col("value")),
            Nov=pl.when(pl.col("month") == 11).then(pl.col("value")),
            Dec=pl.when(pl.col("month") == 12).then(pl.col("value")),
        )
        .select("term", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
        .group_by("term")
        .agg([
            pl.col("Jan").max().alias("Jan"),
            pl.col("Feb").max().alias("Feb"),
            pl.col("Mar").max().alias("Mar"),
            pl.col("Apr").max().alias("Apr"),
            pl.col("May").max().alias("May"),
            pl.col("Jun").max().alias("Jun"),
            pl.col("Jul").max().alias("Jul"),
            pl.col("Aug").max().alias("Aug"),
            pl.col("Sep").max().alias("Sep"),
            pl.col("Oct").max().alias("Oct"),
            pl.col("Nov").max().alias("Nov"),
            pl.col("Dec").max().alias("Dec")
        ])
    )

    return pl.concat([min_monthly_flow, max_monthly_flow, mean_monthly_flow]).collect().to_dicts()

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
            "years": monthly_mean_flow_year,
            "terms": monthly_mean_flow_term
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
        .sort('paramId', 'd')
        .group_by(["paramId", "units", "title"])
        .agg([
            pl.struct(["d", "v"]).alias("data")
        ])
        .select("paramId", "units", "title", "data")
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
