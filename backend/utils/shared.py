import polars as pl

def generate_yearly_metrics(metrics: list[dict], variable_ids: list[int], year: int) -> list[dict]:
    metrics = (
        pl.LazyFrame(
            metrics,
            schema_overrides={
                'station_id': pl.Int32,
                'datestamp': pl.Date,
                'variable_id': pl.Int16,
                'value': pl.Float64
            }
        )
        .filter(
            pl.col("datestamp").dt.year() == year
        )
    )
    # Step 1: Create a LazyFrame of all ordinal days (1 to 366)
    full_days = pl.select(d=pl.arange(1, 366)).lazy()

    # Step 2: Filter and prepare the metric values
    processed = (
        metrics
        .filter(
            pl.col("variable_id").is_in(variable_ids)
        )
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .select(["d", "v"])
    )

    # Step 3: Join full days with processed metrics
    return (
        full_days
        .join(processed, on="d", how="left")
        .sort("d")
    ).collect().to_dicts()
