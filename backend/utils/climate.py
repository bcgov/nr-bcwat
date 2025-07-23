import json
import polars as pl
from utils.shared import generate_yearly_metrics

def generate_current_temperature(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter(
            (pl.col("variable_id").is_in([6, 8]))
        )
        .with_columns(
            d=pl.col("datestamp"),
            max=pl.when(pl.col("variable_id") == 6).then(pl.col("value")),
            min=pl.when(pl.col("variable_id") == 8).then(pl.col("value"))
        )
        .group_by("d").agg([
            pl.col("max").max(),
            pl.col("min").min()
        ])
        .select(["d", "max", "min"])
        .sort("d")
    ).collect().to_dicts()

def generate_historical_temperature(metrics: pl.LazyFrame) -> list[dict]:

    full_days = pl.select(d=pl.arange(1, 367)).lazy()

    processed = (
        metrics
        .filter(
            (pl.col("variable_id").is_in([6, 8]))
        )
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            max=pl.when(pl.col("variable_id") == 6).then(pl.col("value")),
            min=pl.when(pl.col("variable_id") == 8).then(pl.col("value"))
        )
        .group_by("d")
        .agg([
            pl.col("max").quantile(9/10).alias("maxp90"),
            pl.col("max").mean().alias("maxavg"),
            pl.col("min").mean().alias("minavg"),
            pl.col("min").quantile(1/10).alias("minp10")
        ])
        .select("d", "maxp90", "maxavg", "minavg", "minp10")
        .sort("d")
    )

    return (
        full_days
        .join(processed, on="d", how="left")
        .sort("d")
    ).collect().to_dicts()

def generate_current_precipitation(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter(pl.col("variable_id") == 27)
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    ).collect().to_dicts()

def generate_historical_precipitation(metrics: pl.LazyFrame) -> list[dict]:

    full_days = pl.select(d=pl.arange(1, 367)).lazy()

    processed = (
        metrics
        .filter(pl.col("variable_id") == 27)
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .group_by("d")
        .agg([
            pl.col("v").quantile(9/10).alias("p90"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("p50"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").quantile(1/10).alias("p10")
        ])
        .select("d", "p90", "p75", "p50", "p25", "p10")
        .sort("d")
    )

    return (
        full_days
        .join(processed, on="d", how="left")
        .sort("d")
    ).collect().to_dicts()

def generate_current_snow_on_ground_depth(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter((pl.col("variable_id") == 5))
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    ).collect().to_dicts()

def generate_historical_snow_on_ground_depth(metrics: pl.LazyFrame) -> list[dict]:

    full_days = pl.select(d=pl.arange(1, 367)).lazy()

    processed = (
        metrics
        .filter((pl.col("variable_id") == 5))
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .group_by("d")
        .agg([
            pl.col("v").quantile(9/10).alias("p90"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("a"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").quantile(1/10).alias("p10")
        ])
        .select("d", "p90", "p75", "a", "p25", "p10")
        .sort("d")
    )

    return (
        full_days
        .join(processed, on="d", how="left")
        .sort("d")
    ).collect().to_dicts()

def generate_current_snow_water_equivalent(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter((pl.col("variable_id") == 16))
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    ).collect().to_dicts()

def generate_historical_snow_water_equivalent(metrics: pl.LazyFrame) -> list[dict]:

    full_days = pl.select(d=pl.arange(1, 367)).lazy()

    processed = (
        metrics
        .filter((pl.col("variable_id") == 16))
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .group_by("d")
        .agg([
            pl.col("v").quantile(9/10).alias("p90"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("a"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").quantile(1/10).alias("p10")
        ])
        .select("d", "p90", "p75", "a", "p25", "p10")
        .sort("d")
    )

    return (
        full_days
        .join(processed, on="d", how="left")
        .sort("d")
    ).collect().to_dicts()

def generate_current_manual_snow_survey(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter(pl.col("variable_id") == 19)
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value"),
            survey_period=pl.col("survey_period")
        )
        .select(["d", "v", "survey_period"])
        .sort("d", "survey_period")
    ).collect().to_dicts()

def generate_historical_manual_snow_survey(metrics: pl.LazyFrame) -> list[dict]:

    full_days = pl.select(d=pl.arange(1, 367)).lazy()

    processed = (
        metrics
        .filter(pl.col("variable_id") == 19)
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .group_by("d")
        .agg([
            pl.col("v").quantile(9/10).alias("p90"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("p50"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").quantile(1/10).alias("p10")
        ])
        .select("d", "p90", "p75", "p50", "p25", "p10")
        .sort("d")
    )

    return (
        full_days
        .join(processed, on="d", how="left")
        .sort("d")
    ).collect().to_dicts()

def generate_climate_station_metrics(metrics: list[dict]) -> list[dict]:
    raw_metrics_lf = pl.LazyFrame(
            metrics,
            schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.Date
            }
        )

    temperature_current = generate_current_temperature(raw_metrics_lf)
    temperature_historical = generate_historical_temperature(raw_metrics_lf)

    precipitation_current = generate_current_precipitation(raw_metrics_lf)
    precipitation_historical = generate_historical_precipitation(raw_metrics_lf)

    snow_on_ground_depth_current = generate_current_snow_on_ground_depth(raw_metrics_lf)
    snow_on_ground_depth_historical = generate_historical_snow_on_ground_depth(raw_metrics_lf)

    snow_water_equivalent_current = generate_current_snow_water_equivalent(raw_metrics_lf)
    snow_water_equivalent_historical = generate_historical_snow_water_equivalent(raw_metrics_lf)

    manual_snow_survey_current = generate_current_manual_snow_survey(raw_metrics_lf)
    manual_snow_survey_historical = generate_historical_manual_snow_survey(raw_metrics_lf)

    return {
        "temperature": {
            "current": temperature_current,
            "historical": temperature_historical
        },
        "precipitation": {
            "current": precipitation_current,
            "historical": precipitation_historical,
        },
        "snow_on_ground_depth": {
            "current": snow_on_ground_depth_current,
            "historical": snow_on_ground_depth_historical
        },
        "snow_water_equivalent": {
            "current": snow_water_equivalent_current,
            "historical": snow_water_equivalent_historical
        },
        "manual_snow_survey": {
            "current": manual_snow_survey_current,
            "historical": manual_snow_survey_historical
        }
    }
