import polars as pl

get_station_list_default = pl.LazyFrame(
    {
        "original_id": ["A", "B", "C", "D", "E", "F"],
        "station_id": [1, 2, 3, 4, 5, 6],
    }
)
