from etl_pipelines.utils.functions import (
    setup_logging,
    reconnect_if_dead,
    update_station_status_id,
    update_station_variable_table,
    update_station_year_table,
    NoNewStation
)
from etl_pipelines.tests.conftest import MockDbConn
from mock import MagicMock, patch
import logging
import pytest


def test_setup_logging():
    #Ensure that we are only getting a logging.Logger class object when we call this.
    assert isinstance(setup_logging(), logging.Logger)
    assert isinstance(setup_logging('test'), logging.Logger)

def test_reconnect_if_dead():
    fake_db = MockDbConn()
    fake_hook = MagicMock()

    fake_hook.get_conn.return_value = "new_connection"

    # Test that exception does not get raised
    new_conn = reconnect_if_dead(fake_db.conn(), fake_hook)

    assert new_conn == fake_db.conn()

    fake_db.conn().cursor.assert_called_once()

    # Test that exception is raised
    fake_db.conn().cursor.side_effect = Exception

    new_conn = reconnect_if_dead(fake_db.conn(), fake_hook)

    assert new_conn == "new_connection"

    fake_db.conn().close.assert_called_once()


@patch("etl_pipelines.utils.functions.reconnect_if_dead", lambda conn: conn)
def test_update_station_status_id():
    fake_db = MockDbConn()

    # Test that exception is raised with no connection
    with pytest.raises(RuntimeError, match=r"No database connection provided. Please provide a database connection.*"):
        update_station_status_id()

    fake_db.cursor().execute.side_effect = Exception

    # Test that the right exception gets raised if the execute fails:
    with pytest.raises(RuntimeError, match=r"Failed to update station_status_id in the table bcwat_obs\.station.*"):
        update_station_status_id(db_conn=fake_db.conn())

    fake_db.conn().cursor.assert_called_once()
    fake_db.cursor().execute.assert_called_once()
    fake_db.conn().rollback.assert_called_once()
    fake_db.conn().commit.assert_not_called()
    fake_db.cursor().close.assert_called_once()

    # Clean all call stack
    fake_db.reset_mock(reset_effect=True)

    # Call function, expect good execution
    update_station_status_id(fake_db.conn())

    # Test that the right things are called
    fake_db.conn().cursor.assert_called_once()
    fake_db.cursor().execute.assert_called_once()
    fake_db.conn().rollback.assert_not_called()
    fake_db.conn().commit.assert_called_once()
    fake_db.cursor().close.assert_called_once()


@patch("etl_pipelines.utils.functions.reconnect_if_dead", lambda conn: conn)
def test_update_station_variable_table():
    # Test that exception is raised with no connection
    with pytest.raises(RuntimeError, match="No database connection provided. Please provide a database connection.*"):
        update_station_variable_table()

    # Set up mocks
    fake_db = MockDbConn()

    fake_db.cursor().execute.side_effect = Exception

    # Test that the right exception is raised
    with pytest.raises(RuntimeError, match=r"Failed to update station_variable table.*"):
        update_station_variable_table(fake_db.conn())

    fake_db.cursor().execute.assert_called_once()
    fake_db.conn().cursor.assert_called_once()
    fake_db.conn().rollback.assert_called_once()
    fake_db.conn().commit.assert_not_called()

    # Clean up
    fake_db.reset_mock(reset_effect=True)

    # Set up
    fake_db.cursor().execute.side_effect = lambda query: exec("raise Exception") if ("INSERT INTO bcwat_obs.station_water_quality_parameter" in query) else None

    # Test that the second exception is raised
    with pytest.raises(RuntimeError, match=r"Failed to update station_water_quality_parameter table.*"):
        update_station_variable_table(fake_db.conn())

    fake_db.conn().cursor.assert_called_once()
    fake_db.conn().commit.assert_called_once()
    fake_db.conn().rollback.assert_called_once()
    fake_db.cursor().execute.assert_any_call("TRUNCATE bcwat_obs.station_variable;")
    fake_db.cursor().execute.assert_any_call("TRUNCATE bcwat_obs.station_water_quality_parameter;")
    assert fake_db.cursor().execute.call_count == 4
    fake_db.cursor().close.assert_called_once()

    # Clean up
    fake_db.reset_mock(reset_effect=True)

    # Test Successful Execution
    update_station_variable_table(fake_db.conn())

    fake_db.conn().cursor.assert_called_once()
    assert fake_db.conn().commit.call_count == 2
    fake_db.conn().rollback.assert_not_called()
    fake_db.cursor().execute.assert_any_call("TRUNCATE bcwat_obs.station_variable;")
    fake_db.cursor().execute.assert_any_call("TRUNCATE bcwat_obs.station_water_quality_parameter;")
    assert fake_db.cursor().execute.call_count == 4
    fake_db.cursor().close.assert_called_once()

@patch("etl_pipelines.utils.functions.reconnect_if_dead", lambda conn: conn)
def test_update_station_year_table():
    # Test that exception is raised with no connection
    with pytest.raises(RuntimeError, match="No database connection provided. Please provide a database connection.*"):
        update_station_year_table()

    # Set up mocks
    fake_db = MockDbConn()

    fake_db.cursor().execute.side_effect = Exception

    # Test that the right exception is raised
    with pytest.raises(RuntimeError, match=r"Failed to update station_year table.*"):
        update_station_year_table(fake_db.conn())

    fake_db.conn().cursor.assert_called_once()
    fake_db.cursor().execute.assert_called_once()
    fake_db.conn().rollback.assert_called_once()
    fake_db.conn().commit.assert_not_called()
    fake_db.cursor().close.assert_called_once()

    # Clean all call stack
    fake_db.reset_mock(reset_effect=True)

    # Call function, expect good execution
    update_station_status_id(fake_db.conn())

    # Test that the right things are called
    fake_db.conn().cursor.assert_called_once()
    fake_db.cursor().execute.assert_called_once()
    fake_db.conn().rollback.assert_not_called()
    fake_db.conn().commit.assert_called_once()
    fake_db.cursor().close.assert_called_once()

def test_NoNewStation_exception():
    with pytest.raises(NoNewStation, match="this is a test"):
        raise NoNewStation("this is a test")
