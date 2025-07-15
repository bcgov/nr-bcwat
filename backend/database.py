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
                raise Exception({
                    "user_message": "Something went wrong! Please try again later.",
                    "server_message": error_message,
                    "status_code": 500
                })
                # Error in execute function
            finally:
                self.pool.putconn(connection)

        raise Exception({
                    "user_message": "Something went wrong! Please try again later.",
                    "server_message": error_message,
                    "status_code": 500
                })

    def get_stations_by_type(self, **args):
        """
            Build and Return Dictionary of Features that are GeoJson compatible.
        """
        from queries.shared.get_stations_by_type import get_stations_by_type_query

        response = self.execute_as_dict(sql=get_stations_by_type_query, args=args, fetch_one=True)
        return response

    def get_station_by_type_and_id(self, **args):
        from queries.shared.get_station_by_type_and_id import get_station_by_type_and_id

        response = self.execute_as_dict(sql=get_station_by_type_and_id, args=args, fetch_one=True)
        return response

    def get_climate_station_report_by_id(self, **args):
        from queries.climate.get_climate_station_report_by_id import get_climate_station_report_by_id_query

        response = self.execute_as_dict(sql=get_climate_station_report_by_id_query, args=args)
        return response

    def get_groundwater_level_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_level_station_report_by_id import get_groundwater_level_station_report_by_id_query

        response = self.execute_as_dict(sql=get_groundwater_level_station_report_by_id_query, args=args)
        return response

    def get_groundwater_quality_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_quality_station_report_by_id import get_groundwater_quality_station_report_by_id_query

        response = self.execute_as_dict(sql=get_groundwater_quality_station_report_by_id_query, args=args)
        return response

    def get_streamflow_station_report_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_report_by_id import get_streamflow_station_report_by_id_query

        response = self.execute_as_dict(sql=get_streamflow_station_report_by_id_query, args=args)
        return response

    def get_streamflow_station_flow_metrics_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_flow_metrics_by_id import get_streamflow_station_flow_metrics_by_id_query

        response = self.execute_as_dict(sql=get_streamflow_station_flow_metrics_by_id_query, args=args, fetch_one=True)
        return response

    def get_streamflow_station_report_flow_duration_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_report_flow_duration_by_id import get_streamflow_station_report_flow_duration_by_id_query

        return get_streamflow_station_report_flow_duration_by_id_query

    def get_surface_water_station_report_by_id(self, **args):
        from queries.surface_water.get_surface_water_station_report_by_id import get_surface_water_station_report_by_id_query

        response = self.execute_as_dict(sql=get_surface_water_station_report_by_id_query, args=args)
        return response

    def get_watershed_stations(self, **args):
        from queries.watershed.get_watershed_stations import get_watershed_stations_query

        response = self.execute_as_dict(get_watershed_stations_query, args=args, fetch_one=True)
        return response

    def get_watershed_by_lat_lng(self, **args):
        from queries.watershed.get_watershed_by_lat_lng import get_watershed_by_lat_lng_query

        response = self.execute_as_dict(get_watershed_by_lat_lng_query, args=args, fetch_one=True)
        return response

    def get_watershed_station_report_by_id(self, **args):
        from queries.watershed.get_watershed_station_report_by_id import get_watershed_station_report_by_id_query

        response = self.execute_as_dict(get_watershed_station_report_by_id_query, args=args)
        return response
