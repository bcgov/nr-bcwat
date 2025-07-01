import inspect
import os
import psycopg2
import inspect
import polars as pl
import time
from constants import logger
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Database:
    def __init__(self):
        logger.info("Connecting to PostgreSQL Database...")
        port = os.getenv("POSTGRES_PORT")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")
        host = os.getenv("POSTGRES_HOST")
        try:
            self.pool = ThreadedConnectionPool(minconn=1, maxconn=10, host = host, database = database, user = user, password = password, port = port)
            logger.info("Connection Successful.")
        except psycopg2.OperationalError as e:
            logger.info(f"Could not connect to Database: {e}")

    def execute_as_dict(self, sql, args=[], fetch_one = False):
        caller_function_name = inspect.stack()[1].function
        retry_count = 0

        while retry_count < 5:
            connection = self.pool.getconn()
            try:
                with connection.cursor(cursor_factory=RealDictCursor) as conn:
                    # Need to unpack - cant read in a dict. requires list of variables.
                    conn.execute(sql, args)
                    results = None

                    if fetch_one:
                        results = conn.fetchone()
                    else:
                        results = conn.fetchall()

                    connection.commit()
                    return results

            except psycopg2.OperationalError as op_error:
                connection.rollback()
                error_message = f"Caller Function: {caller_function_name} - Exceeded Retry Limit with Error: {op_error}"
                # Gradual Break on psycopg2.OperationalError - retry on SSL errors
                retry_count += 1
                time.sleep(5)
            except Exception as error:
                connection.rollback()
                # Exit While Loop without explicit break
                error_message = f"Caller Function: {caller_function_name} - Error in Execute Function: {error}"
                raise Exception({"user_message": "Database error - see logs",
                                    "server_message": error_message,
                                    "status_code": 500})
                # Error in execute function
            finally:
                self.pool.putconn(connection)

        raise Exception({"user_message": "Database error - see logs",
                            "server_message": error_message,
                            "status_code": 500})

    def execute_as_df(self, sql, schema_override):
        caller_function_name = inspect.stack()[1].function
        try:
            connection = self.pool.getconn()
            df = pl.read_database(
            query=sql,
            connection=connection,
            schema_overrides=schema_override
        )
        except Exception as error:
                connection.rollback()
                # Exit While Loop without explicit break
                error_message = f"Caller Function: {caller_function_name} - Error in Execute Function: {error}"
                raise Exception({"user_message": "Database error - see logs",
                                    "server_message": error_message,
                                    "status_code": 500})
        finally:
                self.pool.putconn(connection)
        return df.lazy()

    def get_climate_station_report_by_id(self, **args):
        from queries.climate.get_climate_station_report_by_id import get_climate_station_report_by_id_query

        return get_climate_station_report_by_id_query

    def get_climate_stations(self):
        from queries.climate.get_climate_stations import get_climate_stations_query

        lazyframe = self.execute_as_df(
            sql=get_climate_stations_query,
            schema_override={
                'id': pl.Int32,
                'name': pl.String,
                'latitude': pl.Float64,
                'longitude': pl.Float64,
                'nid': pl.String,
                'net': pl.Int32,
                'ty': pl.Int32,
                'yr': pl.Int32,
                'area': pl.Float64
            })

        return lazyframe

    def get_groundwater_level_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_level_station_report_by_id import get_groundwater_level_station_report_by_id_query

        return get_groundwater_level_station_report_by_id_query

    def get_groundwater_level_stations(self, **args):
        from queries.groundwater.get_groundwater_level_stations import get_groundwater_level_stations_query

        return get_groundwater_level_stations_query

    def get_groundwater_quality_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_quality_station_report_by_id import get_groundwater_quality_station_report_by_id_query

        return get_groundwater_quality_station_report_by_id_query

    def get_groundwater_quality_stations(self, **args):
        from queries.groundwater.get_groundwater_quality_stations import get_groundwater_quality_stations_query

        return get_groundwater_quality_stations_query

    def get_streamflow_station_report_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_report_by_id import get_streamflow_station_report_by_id_query

        return get_streamflow_station_report_by_id_query

    def get_streamflow_stations(self, **args):
        from queries.streamflow.get_streamflow_stations import get_streamflow_stations_query

        return get_streamflow_stations_query

    def get_surface_water_station_report_by_id(self, **args):
        from queries.surface_water.get_surface_water_station_report_by_id import get_surface_water_station_report_by_id_query

        return get_surface_water_station_report_by_id_query

    def get_streamflow_station_report_flow_duration_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_report_flow_duration_by_id import get_streamflow_station_report_flow_duration_by_id_query

        return get_streamflow_station_report_flow_duration_by_id_query

    def get_surface_water_stations(self, **args):
        from queries.surface_water.get_surface_water_stations import get_surface_water_stations_query

        return get_surface_water_stations_query

    def get_watershed_station_report_by_id(self, **args):
        from queries.watershed.get_watershed_station_report_by_id import get_watershed_station_report_by_id_query

        return get_watershed_station_report_by_id_query

    def get_watershed_stations(self, **args):
        from queries.watershed.get_watershed_stations import get_watershed_stations_query

        return get_watershed_stations_query




