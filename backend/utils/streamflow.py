import polars as pl
from utils.shared import (
    generate_current_time_series,
    generate_historical_time_series
)

def generate_seven_day_flow_current(metrics: pl.LazyFrame) -> list[dict]:
    processed = (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    )

    return generate_current_time_series(processed_metrics=processed)

def generate_seven_day_flow_historical(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .group_by("d")
        .agg([
            pl.col("v").max().alias("max"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("p50"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").min().alias("min")
        ])
        .select("d", "max", "p75", "p50", "p25", "min")
        .sort("d")
    )

    return generate_historical_time_series(processed_metrics=processed)

def generate_flow_duration_monthly_flow(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
        .with_columns(
            m=pl.col("datestamp").dt.month(),
            v=pl.col("value")
        )
        .group_by("m")
        .agg([
            pl.col("v").max().alias("max"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("p50"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").min().alias("min")
        ])
        .sort("m")
    ).collect().to_dicts()

def generate_flow_duration_exceedance(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
        .sort("value", descending=True)
        .with_row_index(name="i")
        .with_columns([
            ((pl.col("i") + 1) / pl.len().alias("N") * 100 ).alias("exceedance"),
            pl.col("value")
        ])
        .select(["value", "exceedance"])
    ).collect().to_dicts()

def generate_flow_duration_total_runoff(metrics: pl.LazyFrame) -> list[dict]:
    year_bounds = (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
        .with_columns(
            year=pl.col("datestamp").dt.year(),
        )
        .select([
            pl.col("year").min().alias("min_year"),
            pl.col("year").max().alias("max_year")])
        .collect()
    )
    min_year, max_year = year_bounds[0, "min_year"], year_bounds[0, "max_year"]

    all_years = pl.LazyFrame({"year": list(range(min_year, max_year + 1))})

    runoff_by_year = (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
        .with_columns(
            year=pl.col("datestamp").dt.year(),
            v=pl.col("value")
        )
        .group_by("year")
        .agg(pl.col("v").sum().alias("value"))
    )

    return (
        all_years
        .join(runoff_by_year, on="year", how="left")
        .fill_null(0)
        .sort("year")
    ).collect().to_dicts()

def generate_monthly_mean_flow_by_year(metrics: pl.LazyFrame) -> list[dict]:
    return (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
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
        .filter(
            pl.col("variable_id") == 1
        )
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
        .filter(
            pl.col("variable_id") == 1
        )
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
        .filter(
            pl.col("variable_id") == 1
        )
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

def generate_stage_current(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
        metrics
        .filter(
            pl.col("variable_id") == 2
        )
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value")
        )
        .select(["d", "v"])
        .sort("d")
    )

    return generate_current_time_series(processed_metrics=processed)

def generate_stage_historical(metrics: pl.LazyFrame) -> list[dict]:

    processed = (
        metrics
        .filter(
            pl.col("variable_id") == 2
        )
        .with_columns(
            d=pl.col("datestamp").dt.ordinal_day(),
            v=pl.col("value")
        )
        .group_by("d")
        .agg([
            pl.col("v").max().alias("max"),
            pl.col("v").quantile(3/4).alias("p75"),
            pl.col("v").quantile(1/2).alias("p50"),
            pl.col("v").quantile(1/4).alias("p25"),
            pl.col("v").min().alias("min")
        ])
        .select("d", "max", "p75", "p50", "p25", "min")
        .sort("d")
    )

    return generate_historical_time_series(processed_metrics=processed)

def generate_flow_duration_tool_metrics(metrics: pl.LazyFrame) -> list[dict]:

    return (
        metrics
        .filter(
            pl.col("variable_id") == 1
        )
        .with_columns(
            d=pl.col("datestamp"),
            v=pl.col("value"),
            y=pl.col("datestamp").dt.year(),
            m=pl.col("datestamp").dt.month()
        )
        .select(["d", "v", "y", "m"])
        .sort("d")
    ).collect().to_dicts()

def generate_streamflow_station_metrics(metrics: list[dict]) -> list[dict]:
    """
        Returns a JSON Object containing all metrics calculated in each sub function.
    """

    raw_metrics_list = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datestamp': pl.Date,
            'variable_id': pl.Int16,
            'value': pl.Float64
        }
    )

    seven_day_flow_current = generate_seven_day_flow_current(raw_metrics_list)
    seven_day_flow_historical = generate_seven_day_flow_historical(raw_metrics_list)

    flow_duration_monthly_flow = generate_flow_duration_monthly_flow(raw_metrics_list)
    flow_duration_exceedance = generate_flow_duration_exceedance(raw_metrics_list)
    flow_duration_runoff = generate_flow_duration_total_runoff(raw_metrics_list)

    monthly_mean_flow_year = generate_monthly_mean_flow_by_year(raw_metrics_list)
    monthly_mean_flow_term = generate_monthly_mean_flow_by_term(raw_metrics_list)

    stage_current = generate_stage_current(raw_metrics_list)
    stage_historical = generate_stage_historical(raw_metrics_list)

    flow_duration_tool = generate_flow_duration_tool_metrics(raw_metrics_list)

    return {
        "sevenDayFlow": {
            "current": seven_day_flow_current,
            "historical": seven_day_flow_historical
        },
        "flowDuration": {
            "monthlyFlowStatistics": flow_duration_monthly_flow,
            "flowDuration": flow_duration_exceedance,
            "totalRunoff": flow_duration_runoff
        },
        "monthlyMeanFlow": {
            "years": monthly_mean_flow_year,
            "terms": monthly_mean_flow_term
        },
        "stage": {
            "current": stage_current,
            "historical": stage_historical
        },
        "flowDurationTool": flow_duration_tool
    }

def generate_filtered_streamflow_station_metrics(metrics: list[dict], start_year=None, end_year=None, month=None) -> list[dict]:
    raw_metrics_list = pl.LazyFrame(
        metrics,
        schema_overrides={
            'station_id': pl.Int32,
            'datestamp': pl.Date,
            'variable_id': pl.Int16,
            'value': pl.Float64
        }
    )

    if month is not None:
        raw_metrics_list = raw_metrics_list.filter(pl.col("datestamp").dt.month() == int(month))
    if start_year is not None:
        raw_metrics_list = raw_metrics_list.filter(pl.col("datestamp").dt.year() >= int(start_year))
    if end_year is not None:
        raw_metrics_list = raw_metrics_list.filter(pl.col("datestamp").dt.year() <= int(end_year))

    flow_duration_monthly_flow = generate_flow_duration_monthly_flow(raw_metrics_list)
    flow_duration_exceedance = generate_flow_duration_exceedance(raw_metrics_list)
    flow_duration_runoff = generate_flow_duration_total_runoff(raw_metrics_list)

    return {
        "monthlyFlowStatistics": flow_duration_monthly_flow,
        "flowDuration": flow_duration_exceedance,
        "totalRunoff": flow_duration_runoff
    }

def generate_flow_metrics(flow_metrics) -> list[dict]:
    return [
        {
            "1": flow_metrics['station_flow_metric']['ipf_1'],
            "2": flow_metrics['station_flow_metric']['ipf_2'],
            "5": flow_metrics['station_flow_metric']['ipf_5'],
            "10": flow_metrics['station_flow_metric']['ipf_10'],
            "20": flow_metrics['station_flow_metric']['ipf_20'],
            "25": flow_metrics['station_flow_metric']['ipf_25'],
            "50": flow_metrics['station_flow_metric']['ipf_50'],
            "100": flow_metrics['station_flow_metric']['ipf_100'],
            "200": flow_metrics['station_flow_metric']['ipf_200'],
            "Parameter": "Instantaneous Peak Flow (m3/s)",
            "1.01": flow_metrics['station_flow_metric']['ipf_1_01'],
            "Years of data": flow_metrics['station_flow_metric']['ipf_yr']
        },
        {
            "1": flow_metrics['station_flow_metric']['amfh_1'],
            "2": flow_metrics['station_flow_metric']['amfh_2'],
            "5": flow_metrics['station_flow_metric']['amfh_5'],
            "10": flow_metrics['station_flow_metric']['amfh_10'],
            "20": flow_metrics['station_flow_metric']['amfh_20'],
            "25": flow_metrics['station_flow_metric']['amfh_25'],
            "50": flow_metrics['station_flow_metric']['amfh_50'],
            "100": flow_metrics['station_flow_metric']['amfh_100'],
            "200": flow_metrics['station_flow_metric']['amfh_200'],
            "Parameter": "Annual Mean Flow (high, m3/s)",
            "1.01": flow_metrics['station_flow_metric']['amfh_1_01'],
            "Years of data": flow_metrics['station_flow_metric']['amfh_yr']
        },
        {
            "1": flow_metrics['station_flow_metric']['amfl_1'],
            "2": flow_metrics['station_flow_metric']['amfl_2'],
            "5": flow_metrics['station_flow_metric']['amfl_5'],
            "10": flow_metrics['station_flow_metric']['amfl_10'],
            "20": flow_metrics['station_flow_metric']['amfl_20'],
            "25": flow_metrics['station_flow_metric']['amfl_25'],
            "50": flow_metrics['station_flow_metric']['amfl_50'],
            "100": flow_metrics['station_flow_metric']['amfl_100'],
            "200": flow_metrics['station_flow_metric']['amfl_200'],
            "Parameter": "Annual Mean Flow (low, m3/s)",
            "1.01": flow_metrics['station_flow_metric']['amfl_1_01'],
            "Years of data": flow_metrics['station_flow_metric']['amfl_yr']
        },
        {
            "1": flow_metrics['station_flow_metric']['js_7df_1'],
            "2": flow_metrics['station_flow_metric']['js_7df_2'],
            "5": flow_metrics['station_flow_metric']['js_7df_5'],
            "10": flow_metrics['station_flow_metric']['js_7df_10'],
            "20": flow_metrics['station_flow_metric']['js_7df_20'],
            "25": flow_metrics['station_flow_metric']['js_7df_25'],
            "50": flow_metrics['station_flow_metric']['js_7df_50'],
            "100": flow_metrics['station_flow_metric']['js_7df_100'],
            "200": flow_metrics['station_flow_metric']['js_7df_200'],
            "Parameter": "June-Sept 7 Day Low Flow (m3/s)",
            "1.01": flow_metrics['station_flow_metric']['js_7df_1_01'],
            "Years of data": flow_metrics['station_flow_metric']['js_7df_yr']
        },
        {
            "1": flow_metrics['station_flow_metric']['ann_7df_1'],
            "2": flow_metrics['station_flow_metric']['ann_7df_2'],
            "5": flow_metrics['station_flow_metric']['ann_7df_5'],
            "10": flow_metrics['station_flow_metric']['ann_7df_10'],
            "20": flow_metrics['station_flow_metric']['ann_7df_20'],
            "25": flow_metrics['station_flow_metric']['ann_7df_25'],
            "50": flow_metrics['station_flow_metric']['ann_7df_50'],
            "100": flow_metrics['station_flow_metric']['ann_7df_100'],
            "200": flow_metrics['station_flow_metric']['ann_7df_200'],
            "Parameter": "June-Sept 7 Day Low Flow (m3/s)",
            "1.01": flow_metrics['station_flow_metric']['ann_7df_1_01'],
            "Years of data": flow_metrics['station_flow_metric']['ann_7df_yr']
        }
    ]

