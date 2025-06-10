import polars as pl

def prepare_lazyframes(streamflow_input):
    fd_lf = pl.LazyFrame(streamflow_input)

    fd_lf = fd_lf.with_columns(
        pl.col("d").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%.3fZ").alias("d"),
        pl.col("v").cast(pl.Float64),
        pl.col("d").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%.3fZ").dt.year().alias("year"),
        pl.col("d").str.to_datetime(format="%Y-%m-%dT%H:%M:%S%.3fZ").dt.month().alias("month"),
    )

    return fd_lf

def compute_total_runoff(fd_lf: pl.LazyFrame) -> pl.LazyFrame:
    year_bounds = (
        fd_lf
        .select([pl.col("year").min().alias("min_year"), pl.col("year").max().alias("max_year")])
        .collect()
    )
    min_year, max_year = year_bounds[0, "min_year"], year_bounds[0, "max_year"]

    all_years = pl.LazyFrame({"year": list(range(min_year, max_year + 1))})

    runoff_by_year = (
        fd_lf
        .group_by("year")
        .agg(pl.col("v").sum().alias("value"))
    )

    return (
        all_years
        .join(runoff_by_year, on="year", how="left")
        .fill_null(0)
        .sort("year")
    )


def compute_monthly_flow_statistics(fd_lf: pl.LazyFrame) -> pl.LazyFrame:
    return (
        fd_lf
        .group_by("month")
        .agg([
            pl.col("v").min().alias("min"),
            pl.col("v").max().alias("max"),
            pl.col("v").median().alias("median"),
            pl.col("v").quantile(0.25, "nearest").alias("p25"),
            pl.col("v").quantile(0.75, "nearest").alias("p75"),
        ])
        .sort("month")
    )


def compute_flow_exceedance(fd_lf: pl.LazyFrame) -> pl.LazyFrame:
    return (
        fd_lf
        .sort("v", descending=True)
        .with_row_index(name="i")
        .with_columns([
            ((pl.col("i") + 1) / pl.len().alias("N") * 100 ).alias("exceedance"),
            pl.col("v").alias("value")
        ])
        .select(["value", "exceedance"])
    )
