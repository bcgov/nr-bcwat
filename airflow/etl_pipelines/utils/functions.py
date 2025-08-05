from etl_pipelines.utils.constants import loggers
import logging

def setup_logging(name = 'airflow'):
    if name in loggers:
        return loggers[name]
    else:
        FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s] [%(funcName)s] [%(lineno)s]: %(message)s"
        logging.basicConfig(format=FORMAT)
        logger = logging.getLogger('airflow')
        logger.setLevel(logging.DEBUG)

        loggers[name] = logger

        return logger

def update_station_year_table(db_conn = None):
    """
    Updates the station_year table in the bcwat_obs schema with the years extracted from
    various observation tables.

    This function aggregates the station_id and the year part of the date from several
    tables (station_observation, water_quality_hourly, and climate_msp) and inserts them
    into the station_year table. If there is a conflict with the primary key, it does nothing
    for the conflicting rows.

    Args:
        db_conn (psycopg2.extensions.connection, optional): The database connection to execute
        the query. Defaults to None.

    Output:
        None
    """

    logger = setup_logging()
    if db_conn == None:
        logger.error(f"No database connection provided. Please provide a database connection.")
        raise RuntimeError(f"No database connection provided. Please provide a database connection.")

    query = """
        WITH years AS (
            SELECT station_id, date_part('year', datestamp)::INTEGER AS year FROM bcwat_obs.station_observation
            UNION
            SELECT station_id, date_part('year', datetimestamp)::INTEGER AS year FROM bcwat_obs.water_quality_hourly
            UNION
            SELECT station_id, date_part('year', datestamp)::INTEGER AS year FROM bcwat_obs.climate_msp
        )
        INSERT INTO bcwat_obs.station_year SELECT * FROM years
        ON CONFLICT ON CONSTRAINT station_year_pkey DO NOTHING;
    """

    try:
        logger.info("Updating station_year table. This will take Approximately 3-5 minutes.")
        cursor = db_conn.cursor()
        cursor.execute(query)
        db_conn.commit()
    except Exception as e:
        db_conn.rollback()
        logger.error(f"Failed to update station_year table. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to update station_year table. Error: {e}")
    finally:
        cursor.close()

    logger.info("Successfully updated station_year table.")

def update_station_variable_table(db_conn = None):
    """
    Updates the station_variable and station_water_quality_parameter tables in the database.

    This function performs the following steps:
    1. Truncates the station_variable table, then populates it by selecting distinct station_id
       and variable_id from the station_observation and climate_msp tables.
    2. Truncates the station_water_quality_parameter table, then populates it by selecting distinct
       station_id and parameter_id from the water_quality_hourly table.

    Args:
        db_conn (psycopg2.connection): The database connection to execute the queries. Defaults to None.

    Output:
        None
    """

    logger = setup_logging()
    if db_conn == None:
        logger.error(f"No database connection provided. Please provide a database connection.")
        raise RuntimeError(f"No database connection provided. Please provide a database connection.")

    variable_query = """
        WITH variables AS (
            SELECT station_id, variable_id FROM bcwat_obs.station_observation
            UNION
            SELECT station_id, variable_id FROM bcwat_obs.climate_msp
        )
        INSERT INTO bcwat_obs.station_variable SELECT * FROM variables
        ON CONFLICT ON CONSTRAINT station_variable_pkey DO NOTHING;
    """

    parameter_query = """
        INSERT INTO bcwat_obs.station_water_quality_parameter
            SELECT DISTINCT ON (station_id, parameter_id) station_id, parameter_id FROM bcwat_obs.water_quality_hourly
        ON CONFLICT ON CONSTRAINT station_water_quality_parameter_pkey DO NOTHING;
    """

    cursor = db_conn.cursor()

    try:
        logger.info("Truncating table before starting")
        cursor.execute("TRUNCATE bcwat_obs.station_variable;")
        logger.info("Updating station_variable table. This will take approximately 2-5 minutes.")
        cursor.execute(variable_query)
        db_conn.commit()
    except Exception as e:
        db_conn.rollback()
        logger.error(f"Failed to update station_variable table. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to update station_variable table. Error: {e}")

    logger.info("Successfully updated station_variable table.")

    try:
        logger.info("Truncating station_water_quality_parameter table before starting")
        cursor.execute("TRUNCATE bcwat_obs.station_water_quality_parameter;")
        logger.info("Updating station_water_quality_parameter table. This will take approximately 2-5 minutes.")
        cursor.execute(parameter_query)
        db_conn.commit()
    except Exception as e:
        db_conn.rollback()
        logger.error(f"Failed to update station_water_quality_parameter table. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to update station_water_quality_parameter table. Error: {e}")
    finally:
        cursor.close()

    logger.info("Successfully updated station_water_quality_parameter table.")


def update_station_status_id(db_conn = None):
    """
    Updates the status_id of stations in the table bcwat_obs.station to 4 for stations that does not have data in the last 3 days in the tables:
    bcwat_obs.station_observation, bcwat_obs.water_quality_hourly, or bcwat_obs.climate_msp.

    Args:
        db_conn (psycopg2.connection): The database connection to execute the query. Defaults to None.

    Output:
        None
    """
    logger = setup_logging()
    if db_conn == None:
        logger.error(f"No database connection provided. Please provide a database connection.")
        raise RuntimeError(f"No database connection provided. Please provide a database connection.")

    query = """
        UPDATE
            bcwat_obs.station
        SET
            station_status_id = 3
        WHERE
            station_status_id = 4;

        UPDATE
            bcwat_obs.station
        SET
            station_status_id = 4
        WHERE
            station_id IN (
                (SELECT
                    station_id
                FROM
                    bcwat_obs.station_observation
                WHERE
                    datestamp >= (now() - '3 days'::INTERVAL)::DATE
                GROUP BY
                    station_id)
                UNION
                (SELECT
                    station_id
                FROM
                    bcwat_obs.water_quality_hourly
                WHERE
                    datetimestamp >= (now() - '3 days'::INTERVAL)::DATE
                GROUP BY
                    station_id)
                UNION
                (SELECT
                    station_id
                FROM
                    bcwat_obs.climate_msp
                WHERE
                    datestamp >= (now() - '3 days'::INTERVAL)::DATE
                GROUP BY
                    station_id)
	        );
    """

    try:
        logger.info("Updating station_status_id in the table bcwat_obs.station. This will take approximately 2-5 minutes.")
        cursor = db_conn.cursor()
        cursor.execute(query)
        db_conn.commit()
        cursor.close()
    except Exception as e:
        db_conn.rollback()
        logger.error(f"Failed to update station_status_id in the table bcwat_obs.station. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to update station_status_id in the table bcwat_obs.station. Error: {e}")

    logger.info("Successfully updated station_status_id in the table bcwat_obs.station.")
