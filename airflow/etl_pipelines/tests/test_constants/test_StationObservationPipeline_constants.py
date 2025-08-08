import polars as pl
from io import StringIO

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

LOAD_TABLE_INTO_DB_DATA = pl.DataFrame({
    "sation_id": [100,200,300,100,200,300,100],
    "datestamp": ["2025-08-07","2025-08-07","2025-08-07","2025-08-06","2025-08-06","2025-08-06","2025-08-05"],
    "variable_id": [1,1,1,2,2,2,1],
    "qa_id": [0,0,0,0,0,0,0],
    "value": [1.0,2.5,3.5,4.10,5.76,6.654,7.23]
})

MAKE_LAZY_FRAME_CASE_1 = b"col1,col2,col3,col4,col5\n,12,var1,-123.6441909494533,55.29809818294311\nvalue,39,var2,-121.898972387,53.2893198\n4493,23,var3,-119.23871982,66.23493890"

MAKE_LAZY_FRAME_CASE_2 = b"col1,col2,col3\ntest,12,var1\nvalue,39,var2\n4493,23,var3"

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

NEW_STATION_CONSTRUCT_INSERT_DATA = pl.LazyFrame({
    "original_id": ["station5"],
    "station_name": ["Station For Testing"],
    "station_status_id": [4],
    "longitude": [-125.21209467692678],
    "latitude": [50.21519901797626],
    "scrape": [True],
    "stream_name": ["Unknown Stream"],
    "station_description": ["Station Description with Meaning"],
    "operation_id": [1],
    "drainage_area": [369.594],
    "regulated": [False],
    "user_flag": [False],
    "year": [[2025]],
    "project_id": [[3,5,6]],
    "network_id": [0],
    "type_id": [1],
    "variable_id": [[1,2]]
})

NEW_STATION_CONSTRUCT_EXPECTED_OUTPUT = pl.DataFrame({
        "original_id": ["station5"],
        "network_id": [0],
        "type_id": [1],
        "station_name": ["Station For Testing"],
        "station_status_id": [4],
        "longitude": [-125.21209467692678],
        "latitude": [50.21519901797626],
        "scrape": [True],
        "stream_name": ["Unknown Stream"],
        "station_description": ["Station Description with Meaning"],
        "operation_id": [1],
        "drainage_area": [369.594],
        "regulated": [False],
        "user_flag": [False],
    })

NEW_STATION_METADATA_EXPECTED_OUTPUT ={
    "bcwat_obs.station_project_id": [
        "project_id",
        pl.DataFrame({
            "original_id": ["station5", "station5", "station5"],
            "project_id": [3,5,6]
        })
    ],
    "bcwat_obs.station_variable": [
        "variable_id",
        pl.DataFrame({
            "original_id": ["station5", "station5"],
            "variable_id": [1,2]
        })
    ],
    "bcwat_obs.station_year": [
        "year",
        pl.DataFrame({
            "original_id": ["station5"],
            "year": [2025]
        })
    ]
}
