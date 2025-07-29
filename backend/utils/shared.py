import polars as pl
from pathlib import Path
from pprint import pformat
from flask import current_app
from datetime import date
from io import StringIO

def generate_current_time_series(processed_metrics: pl.LazyFrame) -> list[dict]:
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
    return (
        full_dates
        .join(processed_metrics, on="d", how="left")
        .sort("d", descending=False)
    ).collect().to_dicts()

def generate_historical_time_series(processed_metrics: pl.LazyFrame) -> list[dict]:
    full_days = pl.select(d=pl.arange(1, 366)).lazy()

    return (
        full_days
        .join(processed_metrics, on="d", how="left")
        .sort("d")
    ).collect().to_dicts()

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

def generate_station_csv(station_metadata: dict, metrics: list[dict]) -> str:
    buffer = StringIO()

    buffer.write(f'# Data Licence Information,"{station_metadata['network_description']}"\n')
    buffer.write('\n')
    buffer.write(f'# Name,{station_metadata['name']}\n')
    buffer.write(f'# Network,{station_metadata['network_name']}\n')
    buffer.write(f'# Status,"{station_metadata['status_name']}"\n')
    buffer.write(f'# Drainage Area,{station_metadata['area']}\n')
    buffer.write(f'# Operation,Not Available\n')
    buffer.write(f'# Latitude,{station_metadata['latitude']}\n')
    buffer.write(f'# Longitude,{station_metadata['longitude']}\n')
    buffer.write(f'# Description,{station_metadata['description']}\n')
    buffer.write( '# QA,"1 - Quality Checked, 0 - Unchecked Quality"\n')
    buffer.write(f'# Date Range,{station_metadata['start_yr']}-{station_metadata['end_yr']}\n')
    buffer.write(f'# Elevation (m),{station_metadata['elevation']}\n')
    buffer.write("\n")  # blank line between metadata and metrics

    # # Write metrics as proper CSV
    buffer.write("Analysis,Datetime,Value,QA\n")

    metrics_lf = pl.LazyFrame(
        metrics,
        schema_overrides={
            'display_name': pl.String,
            'datestamp': pl.Date,
            'value': pl.Float64,
            'qa_id': pl.Int32,
        }
    ).select('display_name', 'datestamp', 'value', 'qa_id').sort('display_name', 'datestamp', descending=[False, False])

    # Write to the buffer instead of a file
    buffer.write(metrics_lf.collect().write_csv(include_header=False))

    return buffer.getvalue()

def write_db_response_to_fixture(subpath, file_name, data):

    fixture_dir = Path(__file__).parent / f"../tests/unit/fixtures/{subpath}"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    metadata_file_path = fixture_dir / f"{file_name}.py"

    with metadata_file_path.open("w", encoding="utf-8") as f:
        f.write("import datetime \n\n")
        f.write("from psycopg2.extras import RealDictRow\n\n")
        f.write(f"{pformat(data, indent=2)}\n")

import datetime

def write_json_response_to_fixture(subpath, filename, data):
    fixture_dir = Path(__file__).parent / f"../tests/unit/fixtures/{subpath}"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    # Flask-style serialization, including date formatting
    json_str = current_app.json.dumps(data, indent=2, ensure_ascii=False)
    with (fixture_dir / f"{filename}.json").open("w", encoding="utf-8") as f:
        f.write(json_str)
