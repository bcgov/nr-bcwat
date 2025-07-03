import polars as pl

def generate_station_metrics(metrics: list[dict]) -> list[dict]:
    raw_metrics_lf = pl.LazyFrame(
            metrics,
            schema_overrides={
                'source': pl.Enum(['precipitation', 'temperature', 'wind', 'msp', 'swe', 'snow_amount', 'snow_depth']),
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64
            }
        )

    temperature_lf = (
        raw_metrics_lf
        .filter(pl.col("source") == "temperature")
        .group_by("datestamp")
        .with_columns([
            pl.col("datestamp").alias('d'),
            pl.col("value").filter('variable_id' == 6).alias("max"),
            pl.col("value").filter('variable_id' == 8).alias("min")
        ])
        # Group By Datestamp
        # Value when Variable ID = 6 = Max
        # Value when Variable ID = 8 = Min
    )
    print(temperature_lf)

    return raw_metrics_lf.collect().to_dicts()
