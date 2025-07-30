import polars as pl
from datetime import date
from utils.shared import (
    generate_current_time_series,
    generate_historical_time_series
)

def generate_current_temperature(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
        metrics
        .filter(pl.col("variable_id").is_in([6, 8]))
        .with_columns(
            d=pl.col("datestamp").cast(pl.Date),
            max=pl.when(pl.col("variable_id") == 6).then(pl.col("value")),
            min=pl.when(pl.col("variable_id") == 8).then(pl.col("value"))
        )
        .group_by("d")
        .agg([
            pl.col("max").max(),
            pl.col("min").min()
        ])
    )

    return generate_current_time_series(processed_metrics=processed)

def generate_historical_temperature(metrics: pl.LazyFrame) -> list[dict]:

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

    return generate_historical_time_series(processed_metrics=processed)

def generate_current_precipitation(metrics: pl.LazyFrame) -> list[dict]:
    """
        Generates the "current" precipitation.
        These are the sum up to the date of the month for the last year up to the first day of the current month of last year.

        Args:
            metrics - lazyframe containing all report data
        Returns:
            Formatted output for placing into a json body of the report endpoint response
    """
    # Create Date Range for Current Time Series
    today = date.today()
    start_date = date(today.year - 1, today.month, 1)

    # Create a full date range frame
    full_dates = pl.LazyFrame(
        pl.date_range(
            start=start_date,
            end=today,
            interval="1d",
            eager=True
        ).alias("d")
    )

    processed = (
        metrics
        .filter(pl.col("variable_id") == 27)
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
    )

    processed = (
        full_dates
        .join(processed, on="d", how="left")
        .sort("d", descending=False)
    )

    processed = (
        processed.
        with_columns(
            month = pl.col("d").dt.month(),
            year = pl.col("d").dt.year()
        )
        .select(
            pl.col("d"),
            pl.col("v").cum_sum().over("year", "month").alias("v")
        )
    )

    return processed.collect().to_dicts()

def generate_historical_precipitation(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
        metrics
        .filter(pl.col("variable_id") == 27)
        .with_columns(
            v=pl.col("value"),
            month=pl.col("datestamp").dt.month(),
            year=pl.col("datestamp").dt.year()
        )
        .group_by("year", "month")
        .agg([
            pl.col("v").sum().alias("month_sum")
        ])
        .group_by("month")
        .agg([
            pl.col("month_sum").quantile(9/10).alias("p90"),
            pl.col("month_sum").quantile(3/4).alias("p75"),
            pl.col("month_sum").quantile(1/2).alias("p50"),
            pl.col("month_sum").quantile(1/4).alias("p25"),
            pl.col("month_sum").quantile(1/10).alias("p10")
        ])
        .sort("month")
    )

    ordinal_days = (pl.LazyFrame(
        pl.date_range(
            start=date(2021, 1, 1), # Chose a non-leap year
            end=date(2021, 12, 31),
            interval="1d",
            eager=True
        ).alias("d")
    ).select([
        pl.col("d").dt.ordinal_day().alias("d"),
        pl.col("d").dt.month().alias("month")
    ])
    )

    result = ordinal_days.join(processed, on="month", how="left").select(["d", 'p90', 'p75', 'p50', 'p25', 'p10'])

    return generate_historical_time_series(processed_metrics=result)

def generate_climate_precipitation_yearly_metrics(metrics: list[dict], year_analysed: int) -> list[dict]:
    """
        Generate the climate precipitation yearly metrics, which will be the total accumulated rainfall for each month of the given year.

        Args:
            metrics - list of dicts from the database
            year - year being analysed
        Returns:
            monthly-filtered data
    """
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

    processed = (
        raw_metrics_lf
        .filter(pl.col("variable_id") == 27)
        .with_columns(
            v=pl.col("value"),
            month=pl.col("datestamp").dt.month(),
            year=pl.col("datestamp").dt.year()
        )
        .filter(pl.col("year") == year_analysed)
        .group_by("month")
        .agg([
            pl.col("v").sum().alias("v")
        ])
    )

    ordinal_days = (pl.LazyFrame(
        pl.date_range(
            start=date(2021, 1, 1),
            end=date(2021, 12, 31),
            interval="1d",
            eager=True
        ).alias("d")
    ).select([
        pl.col("d").dt.ordinal_day().alias("d"),
        pl.col("d").dt.month().alias("month")
    ])
    )

    result = ordinal_days.join(processed, on="month", how="left")

    return generate_historical_time_series(processed_metrics=result)

def generate_current_snow_on_ground_depth(metrics: pl.LazyFrame) -> list[dict]:
    processed = (
        metrics
        .filter((pl.col("variable_id") == 5))
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    )

    return generate_current_time_series(processed_metrics=processed)

def generate_historical_snow_on_ground_depth(metrics: pl.LazyFrame) -> list[dict]:

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

    return generate_historical_time_series(processed_metrics=processed)

def generate_current_snow_water_equivalent(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
        metrics
        .filter((pl.col("variable_id") == 16))
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    )

    return generate_current_time_series(processed_metrics=processed)

def generate_historical_snow_water_equivalent(metrics: pl.LazyFrame) -> list[dict]:

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

    return generate_historical_time_series(processed_metrics=processed)

def generate_current_manual_snow_survey(metrics: pl.LazyFrame) -> list[dict]:
    processed = (
        metrics
        .filter(pl.col("variable_id") == 19)
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value"),
            survey_period=pl.col("survey_period")
        )
        .select(["d", "v", "survey_period"])
        .sort("d", "survey_period", descending=[True, False])
    )

    return generate_current_time_series(processed_metrics=processed)

def generate_historical_manual_snow_survey(metrics: pl.LazyFrame) -> list[dict]:

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

    return generate_historical_time_series(processed_metrics=processed)

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
