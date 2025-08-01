import inspect
import os
import psycopg2
import inspect
import time
from constants import logger
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Database:
    def __init__(self):
        logger.info("Connecting to PostgreSQL Database...")
        port = os.getenv("POSTGRES_PORT")
        user = os.getenv("POSTGRES_USER")
        self.password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")
        host = os.getenv("POSTGRES_HOST")
        uri = f'postgresql+psycopg2://{user}:{self.password}@{host}:{port}/{database}'
        try:
            self.engine = create_engine(
                uri,
                poolclass= QueuePool,
                pool_size=5,
                max_overflow=2,
                pool_timeout=30,
                pool_pre_ping=True,
                pool_recycle=600,
            )
            self.execute_as_dict('SELECT 1;')
            logger.info("Connection Successful.")
        except psycopg2.OperationalError as e:
            logger.info(f"Could not connect to Database: {str(e).replace(self.password, 'REDACTED')}")

    def execute_as_dict(self, sql, args=[], fetch_one = False):
        caller_function_name = inspect.stack()[1].function
        retry_count = 0
        error_message = None
        while retry_count < 5:

            with self.engine.connect() as conn:
                transaction = conn.begin()
                # Need to unpack - cant read in a dict. requires list of variables.

                try:
                    result = conn.execute(text(sql), args)
                    transaction.commit()
                    results = None

                    if fetch_one:
                        results = result.mappings().first()

                    else:
                        results = result.all()
                        results = [row._asdict() for row in results]
                    return results

                except OperationalError as op_error:
                    transaction.rollback()
                    error_message = f"Caller Function: {caller_function_name} - Exceeded Retry Limit with Error: {str(op_error).replace(self.password, 'REDACTED')}"
                    # Gradual Break on psycopg2.OperationalError - retry on SSL errors
                    retry_count += 1
                    time.sleep(5)

                except SQLAlchemyError as error:
                    transaction.rollback()
                    # Exit While Loop without explicit break
                    error_message = f"Caller Function: {caller_function_name} - Error in Execute Function: {str(error).replace(self.password, 'REDACTED')}"
                    raise Exception({
                        "user_message": "Something went wrong! Please try again later.",
                        "server_message": error_message,
                        "status_code": 500
                    })

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

    def get_station_csv_metadata_by_type_and_id(self, **args):
        from queries.shared.get_station_csv_metadata_by_type_and_id import get_station_csv_metadata_by_type_and_id_query

        response = self.execute_as_dict(sql=get_station_csv_metadata_by_type_and_id_query, args=args, fetch_one=True)
        return response

    def get_climate_station_report_by_id(self, **args):
        from queries.climate.get_climate_station_report_by_id import get_climate_station_report_by_id_query

        response = self.execute_as_dict(sql=get_climate_station_report_by_id_query, args=args)
        return response

    def get_climate_station_csv_by_id(self, **args):
        from queries.climate.get_climate_station_csv_by_id import get_climate_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_climate_station_csv_by_id_query, args=args)
        return response

    def get_groundwater_level_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_level_station_report_by_id import get_groundwater_level_station_report_by_id_query

        response = self.execute_as_dict(sql=get_groundwater_level_station_report_by_id_query, args=args)
        return response

    def get_groundwater_level_station_csv_by_id(self, **args):
        from queries.groundwater.get_groundwater_level_station_csv_by_id import get_groundwater_level_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_groundwater_level_station_csv_by_id_query, args=args)
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

    def get_streamflow_station_csv_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_csv_by_id import get_streamflow_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_streamflow_station_csv_by_id_query, args=args)
        return response

    def get_surface_water_station_report_by_id(self, **args):
        from queries.surface_water.get_surface_water_station_report_by_id import get_surface_water_station_report_by_id_query

        response = self.execute_as_dict(sql=get_surface_water_station_report_by_id_query, args=args)
        return response

    def get_watershed_licences(self, **args):
        from queries.watershed.get_watershed_licences import get_watershed_licences_query

        response = self.execute_as_dict(get_watershed_licences_query , args=args, fetch_one=True)
        return response

    def get_watershed_by_lat_lng(self, **args):
        from queries.watershed.get_watershed_by_lat_lng import get_watershed_by_lat_lng_query

        response = self.execute_as_dict(get_watershed_by_lat_lng_query, args=args, fetch_one=True)
        return response

    def get_watershed_by_id(self, **args):
        from queries.watershed.get_watershed_by_id import get_watershed_by_id_query

        response = self.execute_as_dict(sql=get_watershed_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_report_by_id(self, **args):
        from queries.watershed.get_watershed_report_by_id import get_watershed_report_by_id_query

        response = self.execute_as_dict(get_watershed_report_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_region_by_id(self, **args):
        from queries.watershed.get_watershed_region_by_id import get_watershed_region_by_id_query

        response = self.execute_as_dict(get_watershed_region_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_by_search_term(self, **args):
        from queries.watershed.get_watershed_by_search_term import get_watershed_by_search_term_query

        response = self.execute_as_dict(get_watershed_by_search_term_query, args=args)
        return response

    def get_watershed_licences_by_search_term(self, **args):
        from queries.watershed.get_watershed_licences_by_search_term import get_watershed_licences_by_search_term_query

        response = self.execute_as_dict(get_watershed_licences_by_search_term_query, args=args)
        return response

    def get_watershed_candidates_by_id(self, **args):
        from queries.watershed.get_watershed_candidates_by_id import get_watershed_candidates_by_id_query

        response = self.execute_as_dict(get_watershed_candidates_by_id_query, args=args)
        return response

    def get_watershed_monthly_hydrology_by_id(self, **args):
        from queries.watershed.get_watershed_monthly_hydrology_by_id import get_watershed_monthly_hydrology_by_id_query

        response = self.execute_as_dict(get_watershed_monthly_hydrology_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_allocations_by_id(self, **args):
        from queries.watershed.get_watershed_allocations_by_id import get_watershed_allocations_by_id_query

        response = self.execute_as_dict(get_watershed_allocations_by_id_query, args=args)
        return response

    def get_watershed_industry_allocations_by_id(self, **args):
        from queries.watershed.get_watershed_industry_allocations_by_id import get_watershed_industry_allocations_by_id_query

        response = self.execute_as_dict(get_watershed_industry_allocations_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_bus_stops_by_id(self, **args):
        from queries.watershed.get_watershed_bus_stops_by_id import get_bus_stops_query

        response = self.execute_as_dict(get_bus_stops_query, args=args)
        return response

    def get_watershed_hydrologic_variability_by_id(self, **args):
        from queries.watershed.get_watershed_hydrologic_variability_by_id import get_watershed_hydrologic_variability_by_id_query

        response = self.execute_as_dict(get_watershed_hydrologic_variability_by_id_query, args=args)
        return response

    def get_watershed_annual_hydrology_by_id(self, **args):
        from queries.watershed.get_watershed_annual_hydrology_by_id import get_watershed_annual_hydrology_by_id_query

        response = self.execute_as_dict(get_watershed_annual_hydrology_by_id_query, args=args, fetch_one=True)
        return response

    def get_licence_import_dates(self, **args):
        from queries.watershed.get_licence_import_dates import get_licence_import_dates_query

        response = self.execute_as_dict(get_licence_import_dates_query, args=args)
        return response

    def get_water_quality_station_statistics(self, **args):
        from queries.shared.get_water_quality_station_statistics import get_water_quality_station_statistics_query

        response = self.execute_as_dict(get_water_quality_station_statistics_query, args=args, fetch_one=True)
        return response

    def get_water_quality_station_csv_by_id(self, **args):
        from queries.shared.get_water_quality_csv_data_by_station_id import get_water_quality_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_water_quality_station_csv_by_id_query, args=args)
        return response
