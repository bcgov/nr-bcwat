import polars as pl

def get_station_list_read_database(query, connection, schema_overrides):
    if "''" in query:
        return False
    elif connection != "test_connection":
        return False
    elif schema_overrides != {"original_id": pl.String, "station_id": pl.Int64}:
        return False
    else:
        return pl.DataFrame({
            "original_id": ["station1", "station2", "station3"],
            "station_id": [100, 200, 300]
        })


CHECK_FOR_NEW_STATIONS_DATA = {
    "station_data1":pl.LazyFrame({
        "col1": ["station1", "station2", "station3", "station4"],
        "col2": [12, 24, 36, 48],
        "col3": ["var1", "var2", "var3", "var4"],
        "col4": [-123.6441909494533,-123.36298207866807,-127.29990626966048,-113.155100069166],
        "col5": [55.29809818294311,57.49186839504992,56.94374570420635,60.33580167081925]
    }),
    "station_data2": pl.LazyFrame({
        "col1": ["station3", "station5", "station3", "station4"],
        "col2": [11, 33, 22, 44],
        "col3": ["var4", "var2", "var3", "var4"],
        "col4": [-127.29990626966048,-125.21209467692678,-127.29990626966048,-113.155100069166],
        "col5": [56.94374570420635,50.21519901797626,56.94374570420635,60.33580167081925]
    })
}

