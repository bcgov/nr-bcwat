from mock import MagicMock
from etl_pipelines.tests.test_constants.shared_constants import(
    water_management_district_area
)
import pytest
import polars as pl


class MockDbConn():
    def __init__(self):
        self.__cursor = MagicMock(name="cursor")
        self.__conn = MagicMock(name="conn")

        self.__conn.cursor.return_value = self.__cursor

    def cursor(self):
        return self.__cursor

    def conn(self):
        return self.__conn

    def reset_mock(self, reset_value=False, reset_effect=False):
        self.__cursor.reset_mock(return_value=reset_value, side_effect=reset_effect)
        self.__conn.reset_mock()

def mock_get_whole_table(table_name, has_geom = False):
    if table_name == "wls_water_approval_deanna":
        return (
            pl.scan_csv(
                source="etl_pipelines/tests/test_constants/water_licence_csv/wls_water_approval_deanna.csv",
                has_header=True
            )
            .with_columns(
                pl.col("appfileno").cast(pl.String)
            )
        )
    elif table_name == "bc_wls_water_approval":
        return pl.scan_csv(
            source="etl_pipelines/tests/test_constants/water_licence_csv/bc_wls_water_approval.csv",
            has_header=True
        )
    elif table_name == "water_management_district_area":
        return water_management_district_area
