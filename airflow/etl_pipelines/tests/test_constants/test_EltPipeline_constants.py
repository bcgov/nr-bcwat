import polars as pl

expected_dtype = {
        "ID": pl.String,
        "Date": pl.String,
        "Water Level / Niveau d'eau (m)": pl.Float64,
        "Grade": pl.String,
        "Symbol / Symbole": pl.String,
        "QA/QC": pl.Int64,
        "Discharge / Débit (cms)": pl.Float64,
        "Grade_duplicated_0": pl.String,
        "Symbol / Symbole_duplicated_0": pl.String,
        "QA/QC_duplicated_0": pl.Int64
        }

validate_data_case_2 = pl.LazyFrame(
    {
        "ID": ["01AB001"],
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
        "ID": ["01AB001"],
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
        "ID": ["01AB001"],
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
    schema_overrides=expected_dtype,
    strict=False
)
