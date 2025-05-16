from util import (
    get_from_conn,
    get_to_conn,
    get_wet_conn,
    special_variable_function
)
from constants import (
    non_static_tablename_dict,
    populate_dict,
    logger,
    climate_var_id_conversion
)
from queries.post_import_queries import post_import_query
from dotenv import load_dotenv, find_dotenv
from psycopg2.extras import execute_values, RealDictCursor
import psycopg2 as pg2
import pandas as pd
import numpy as np
import json

def move_non_scraped_data(to_conn):
    from_conn = None
    to_cur = to_conn.cursor()


    for tablename in non_static_tablename_dict:
        table = non_static_tablename_dict[tablename][0]
        query = non_static_tablename_dict[tablename][1]
        schema = non_static_tablename_dict[tablename][2]

        try:
            logger.debug("Truncating Destination Table before insert")
            to_cur.execute(f"TRUNCATE TABLE {schema}.{table} CASCADE;")
            to_conn.commit()
        except Exception as e:
            logger.error(f"Something went wrong truncating the destination table!", exc_info=True)
            to_conn.rollback()
            to_conn.close()
            from_conn.rollback()
            from_conn.close()
            raise RuntimeError
        try:
            logger.debug("Checking if the wet schema on bcwt-staging is required")
            if 'wet' in query:
                from_conn = get_wet_conn()
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)
            else:
                from_conn = get_from_conn()
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)

            logger.debug(f"Getting data from the table {tablename}")
            from_cur.execute(query)
            records = pd.DataFrame(from_cur.fetchmany(1000000))

            if tablename == "variables":
                records = special_variable_function(records)

            while len(records) != 0:
                records.replace({np.nan:None}, inplace=True)
                for col_types in from_cur.description:
                    if col_types[1] == 114:
                        records[col_types[0]] = records[col_types[0]].apply(json.dumps)
                columns = records.columns.to_list()
                insert_tuple = records.to_records(index=False).tolist()

                insert_query =f'''INSERT INTO {schema}.{table}({','.join(columns)}) VALUES %s'''

                logger.debug(f"Inserting large table {tablename} into {schema}.{table}")

                execute_values(to_cur, insert_query, insert_tuple)

                records = pd.DataFrame(from_cur.fetchmany(1000000))

            to_conn.commit()

        except Exception as e:
            logger.error(f"Something went wrong inserting the large tables!", exc_info=True)
            to_conn.rollback()
            to_conn.close()
            from_conn.rollback()
            from_conn.close()
            raise RuntimeError

def populate_other_station_tables( to_conn):
    from_conn = None
    to_cur = to_conn.cursor(cursor_factory = RealDictCursor)

    for key in populate_dict.keys():
        table = populate_dict[key][0]
        query = populate_dict[key][1]
        schema = populate_dict[key][2]
        try:
            logger.debug("Truncating Destination Table before insert")
            to_cur.execute(f"TRUNCATE TABLE {schema}.{table} CASCADE;")
            to_conn.commit()
        except Exception as e:
            logger.error(f"Something went wrong truncating the destination table!", exc_info=True)
            to_conn.rollback()
            to_conn.close()
            from_conn.rollback()
            from_conn.close()
            raise RuntimeError

        try:
            logger.debug(f"Checking if the wet schema on bcwt-staging is required for {key}")
            if 'wet' in query:
                from_conn = get_wet_conn()
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)
            elif "bcwat" in query:
                from_conn = to_conn
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)
            else:
                from_conn = get_from_conn()
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)

            logger.debug(f"Getting data from the table query")
            from_cur.execute(query)
            records = pd.DataFrame(from_cur.fetchmany(1000000))

            if key == "climate_station_variable":
                logger.debug(f"{key} detected, this requires some conversions")
                records = records.replace({"variable_id": climate_var_id_conversion})
                records = records.loc[records["variable_id"] <= 29, : ]

            if key == "water_station_variable":
                logger.debug(f"Removing variables not used in prod for {key}")
                records = records.loc[records["variable_id"] <= 3, : ]

            if 'bcwat' not in query:
                logger.debug(f"Getting station_id from destination table")
                to_cur.execute(f"SELECT original_id, station_id FROM bcwat_obs.station")
                station = pd.DataFrame(to_cur.fetchall())
                logger.debug(f"Joining the two tables together.")

                records = station.merge(records, on="original_id", how="inner").drop("original_id", axis=1)

            columns = records.columns.to_list()
            insert_tuple = records.to_records(index=False).tolist()

            insert_query =f'''INSERT INTO {schema}.{table}({','.join(columns)}) VALUES %s'''

            logger.debug(f"Inserting queried data into {schema}.{table}")

            execute_values(to_cur, insert_query, insert_tuple)
        except Exception as e:
            logger.error(f"Something went wrong inserting the large tables!", exc_info=True)
            to_conn.rollback()
            to_conn.close()
            from_conn.rollback()
            from_conn.close()
            raise RuntimeError

        to_conn.commit()

def run_post_import_queries(to_conn):
    cursor = to_conn.cursor()

    cursor.execute(post_import_query)

    to_conn.commit()

    cursor.close()

def import_non_scraped_data():
    logger.debug("Connecting to To database")
    to_conn = get_to_conn()

    logger.debug("Importing tables in the non_static_table_name_dict dictionary")
    move_non_scraped_data(to_conn)

    logger.debug("Importing tables in the populate_dict dictionary")
    populate_other_station_tables(to_conn)

    logger.debug("Running post import queries")
    run_post_import_queries(to_conn)

    to_conn.close()
