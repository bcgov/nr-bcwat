import polars as pl
import json
from pathlib import Path
from pprint import pformat
import datetime
from flask import current_app

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
