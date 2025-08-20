from mock import MagicMock
import pytest

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
