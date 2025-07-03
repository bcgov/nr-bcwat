import polars as pl

def generate_current_temperature(metrics: pl.LazyFrame) -> pl.LazyFrame:
    return (
        metrics
        .filter(
            (pl.col("variable_id") == 6) | (pl.col("variable_id") == 8)
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

def generate_historical_temperature(metrics: pl.LazyFrame) -> pl.LazyFrame:
    return (
        metrics
        .filter((pl.col("variable_id") == 6) | (pl.col("variable_id") == 8))
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
    ).collect().to_dicts()

def generate_current_precipitation(metrics: pl.LazyFrame) -> pl.LazyFrame:
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

def generate_historical_precipitation(metrics: pl.LazyFrame) -> pl.LazyFrame:
    return (
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
    ).collect().to_dicts()

def generate_current_snow_on_ground_depth(metrics: pl.LazyFrame) -> pl.LazyFrame:
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

def generate_historical_snow_on_ground_depth(metrics: pl.LazyFrame) -> pl.LazyFrame:
    return (
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
    ).collect().to_dicts()

def generate_current_snow_water_equivalent(metrics: pl.LazyFrame) -> pl.LazyFrame:
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

def generate_historical_snow_water_equivalent(metrics: pl.LazyFrame) -> pl.LazyFrame:
    return (
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
    ).collect().to_dicts()

def generate_current_manual_snow_survey(metrics: pl.LazyFrame) -> pl.LazyFrame:
    return (
        metrics
        .filter(pl.col("variable_id") == 19)
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value"),
            survey_period=pl.col("survey_period")
        )
        .select(["d", "v", "survey_period"])
        .sort("d")
    ).collect().to_dicts()

def generate_historical_manual_snow_survey(metrics: pl.LazyFrame) -> pl.LazyFrame:
    return (
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
    ).collect().to_dicts()

def generate_station_metrics(metrics: list[dict]) -> list[dict]:
    raw_metrics_lf = pl.LazyFrame(
            metrics,
            schema_overrides={
                'source': pl.Enum(['precipitation', 'temperature', 'wind', 'msp', 'swe', 'snow_amount', 'snow_depth']),
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64,
                'survey_period': pl.String
            }
        )

    temperature_current_lf = generate_current_temperature(raw_metrics_lf)
    temperature_historical_lf = generate_historical_temperature(raw_metrics_lf)

    precipitation_current_lf = generate_current_precipitation(raw_metrics_lf)
    precipitation_historical_lf = generate_historical_precipitation(raw_metrics_lf)

    snow_on_ground_depth_current_lf = generate_current_snow_on_ground_depth(raw_metrics_lf)
    snow_on_ground_depth_historical_lf = generate_historical_snow_on_ground_depth(raw_metrics_lf)

    snow_water_equivalent_current_lf = generate_current_snow_water_equivalent(raw_metrics_lf)
    snow_water_equivalent_historical_lf = generate_historical_snow_water_equivalent(raw_metrics_lf)

    manual_snow_survey_current_lf = generate_current_manual_snow_survey(raw_metrics_lf)
    manual_snow_survey_historical_lf = generate_historical_manual_snow_survey(raw_metrics_lf)

    return {
        "temperature": {
            "current": temperature_current_lf,
            "historical": temperature_historical_lf
        },
        "precipitation": {
            "current": precipitation_current_lf,
            "historical": precipitation_historical_lf,
        },
        "snow_on_ground_depth": {
            "current": snow_on_ground_depth_current_lf,
            "historical": snow_on_ground_depth_historical_lf
        },
        "snow_water_equivalent": {
            "current": snow_water_equivalent_current_lf,
            "historical": snow_water_equivalent_historical_lf
        },
        "manual_snow_survey": {
            "current": manual_snow_survey_current_lf,
            "historical": manual_snow_survey_historical_lf
        }
    }
