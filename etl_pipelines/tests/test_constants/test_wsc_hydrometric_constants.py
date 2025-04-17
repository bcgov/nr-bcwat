import polars as pl
from utils.constants import WSC_DTYPE_SCHEMA

transform_case_2 = pl.LazyFrame(
    {
        " ID": ["01AB001", "01AB002"],
        "Date": ["2025-04-16T00:00:00-08:00", "2025-04-16T00:00:00-08:00"],
        "Water Level / Niveau d'eau (m)": [1.0, 2.0],
        "Discharge / Débit (cms)": [1.0, 2.0]
    }
)

transform_case_3 = pl.LazyFrame(
    {
        " ID": ["01AB001", "01AB001", "01AB001", "01AB001", "01AB001", "01AB002", "01AB002", "01AB002", "01AB002", "01AB002"],
        "Water Level / Niveau d'eau (m)": [1.0, 2.0, 3, 4, 5, 6, 7, 8, 9, 10],
        "Discharge / Débit (cms)": [1.0, 2.0, 3, 4, 5, 6, 7, 8, 9, 10]
    }
)

transform_case_4 = pl.LazyFrame(
    {
        " ID": ["01AB001", "01AB001", "01AB001", "01AB001", "01AB001", "01AB002", "01AB002", "01AB002", "01AB002", "01AB002"],
        "Date": ["2025-04-16T00:00:00-08:00", "2025-04-16T06:00:00-08:00", "2025-04-16T12:00:00-08:00", "2025-04-16T18:00:00-08:00", "2025-04-17T00:00:00-08:00", "2025-04-16T00:00:00-08:00", "2025-04-16T06:00:00-08:00", "2025-04-16T12:00:00-08:00", "2025-04-16T18:00:00-08:00", "2025-04-17T00:00:00-08:00"],
        "Water Level / Niveau d'eau (m)": [1.0, 2.0, 3, 4, 5, 6, 7, 8, 9, 10],
        "Discharge / Débit (cms)": [1.0, 2.0, 3, 4, 5, 6, 7, 8, 9, 10]
    }
)

transform_case_5 = pl.LazyFrame(
    {
        " ID": ["01AB001", "01AB001", "01AB001", "01AB001", "01AB001", "01AB002", "01AB002", "01AB002", "01AB002", "01AB002"],
        "Date": ["2025-04-16T00:00:00-08:00", "2025-04-16T06:00:00-08:00", "2025-04-16T12:00:00-08:00", "2025-04-16T18:00:00-08:00", "2025-04-17T00:00:00-08:00", "2025-04-16T00:00:00-08:00", "2025-04-16T06:00:00-08:00", "2025-04-16T12:00:00-08:00", "2025-04-16T18:00:00-08:00", "2025-04-17T00:00:00-08:00"],
        "Water Level / Niveau d'eau (m)": [1.0, 2.0, 3, 4, 2.5, 4, 1, None, None, None],
        "Discharge / Débit (cms)": [None, None, None, None, 5, 6, 3, None, 6, None]
    }
)

transform_case_station_id = pl.LazyFrame(
    {
        "original_id": ["01AB001", "01AB002"],
        "station_id": [123, 456]
    }
)


validate_data_case_2 = pl.LazyFrame(
    {
        " ID": ["01AB001"],
        "DateTime": ["2025-04-16T00:00:00-08:00"],
        "Water Level / Niveau d'eau (m)": [1.001],
        "Grade": [None],
        "Symbol / Symbole": [None],
        "QA/QC": [0],
        "Discharge / Débit (cms)": [1.01001],
        "Grade_duplicated_0": [None],
        "Symbol / Symbole_duplicated_0": [None],
        "QA/QC_duplicated_0": [0]
    }
)

validate_data_case_3 = pl.LazyFrame(
    {
        " ID": ["01AB001"],
        "Date": ["2025-04-16T00:00:00-08:00"],
        "Water Level / Niveau d'eau (m)": [1.001],
        "Grade": [1],
        "Symbol / Symbole": [None],
        "QA/QC": [0],
        "Discharge / Débit (cms)": [1.01001],
        "Grade_duplicated_0": [None],
        "Symbol / Symbole_duplicated_0": [None],
        "QA/QC_duplicated_0": [0]
    }
)

validate_data_case_4 = pl.LazyFrame(
    {
        " ID": ["01AB001"],
        "Date": ["2025-04-16T00:00:00-08:00"],
        "Water Level / Niveau d'eau (m)": [1.001],
        "Grade": [""],
        "Symbol / Symbole": [""],
        "QA/QC": [0],
        "Discharge / Débit (cms)": [1.01001],
        "Grade_duplicated_0": [""],
        "Symbol / Symbole_duplicated_0": [""],
        "QA/QC_duplicated_0": [0]
    },
    schema_overrides=WSC_DTYPE_SCHEMA,
    strict=False
)
