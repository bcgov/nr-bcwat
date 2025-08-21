from etl_pipelines.utils.constants import(
    ENV_AQN_DTYPE_SCHEMA
)
import polars as pl

downloaded_data = {
    "temperature": pl.LazyFrame(
        {
            "DATE_PST": ["2025-08-21 00:00", "2025-08-21 01:00", "2025-08-21 01:00", "2025-08-20 00:00", "2025-08-21 02:00", "2025-08-21 03:00", "2025-08-20 00:00", "2025-08-21 01:00", "2025-08-20 00:00", "2025-08-19 00:00"],
            "STATION_NAME":["A", "A", "B", "A", "K", "B", "C", "D", "D", "D"],
            "RAW_VALUE": [-80.0, 80.0, 3.0, None, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "REPORTED_VALUE": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "INSTRUMENT": [None, None, None, None, None, None, None, None, None, None],
            "UNITS": ["C", "C", "C", "C", "C", "C", "C", "C", "C", "C"],
            "PARAMETER": ["TEMP", "TEMP", "TEMP", "TEMP", "TEMP", "TEMP", "TEMP", "TEMP", "TEMP", "TEMP"],
            "EMS_ID": ["A", "A", "B", "A", "K", "B", "C", "D", "D", "D"],
            "LATITUDE": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "LONGITUDE": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        },
        schema_overrides=ENV_AQN_DTYPE_SCHEMA["temperature"]
    ),
    "precipitation": pl.LazyFrame(
        {
            "DATE_PST": ["2025-08-21 00:00", "2025-08-21 01:00", "2025-08-21 01:00", "2025-08-20 00:00", "2025-08-21 02:00", "2025-08-21 03:00", "2025-08-20 00:00", "2025-08-21 01:00", "2025-08-20 00:00", "2025-08-19 00:00"],
            "STATION_NAME":["A", "A", "B", "A", "K", "B", "C", "D", "D", "D"],
            "RAW_VALUE": [-213.0, 21656, 3.0, None, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "REPORTED_VALUE": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "INSTRUMENT": [None, None, None, None, None, None, None, None, None, None],
            "UNITS": ["mm", "mm", "mm", "mm", "mm", "mm", "mm", "mm", "mm", "mm"],
            "PARAMETER": ["PRECIP", "PRECIP", "PRECIP", "PRECIP", "PRECIP", "PRECIP", "PRECIP", "PRECIP", "PRECIP", "PRECIP"],
            "EMS_ID": ["A", "A", "B", "A", "K", "B", "C", "D", "D", "D"],
            "LATITUDE": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "LONGITUDE": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        },
        schema_overrides=ENV_AQN_DTYPE_SCHEMA["precipitation"]
    )
}
