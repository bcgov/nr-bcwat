from util import (
    get_from_conn,
    get_to_conn,
    get_wet_conn,
    special_variable_function
)
from constants import (
    bcwat_obs_data,
    bcwat_licence_data,
    logger,
    climate_var_id_conversion
)
from queries.post_import_queries import post_import_query
from psycopg2.extras import execute_values, RealDictCursor
import psycopg2 as pg2
import pandas as pd
import numpy as np
import json

def populate_all_tables(to_conn, insert_dict):
    """
    Populate all tables in the destination database with data from the source database.

    This function will loop through a dictionary where the keys are the table names and the values are a list of four arguments.
    The four arguments are the table name, the sql query to get the data from the source database, the schema of the table and
    whether or not a join is needed to get the correct station_ids.

    The function will first truncate the destination table, then it will get the data from the source database and finally it
    will insert the data into the destination database. If the table is the climate or water station variables, it will
    remove the variables that are not needed in the prod database. If the table is the variables, it will convert the variable
    ids and names to the correct format. If the table is a station metadata table, it will join the station_id from the
    destination database with the original_id from the source database.

    Args:
        to_conn (psycopg2.extensions.connection): The connection to the destination database.
        insert_dict (dict): A dictionary where the keys are the table names and the values are a list of four arguments.
    """

    from_conn = None
    to_cur = to_conn.cursor(cursor_factory = RealDictCursor)

    for key in insert_dict.keys():
        # Read all dictionary values and assign them to variables
        table = insert_dict[key][0]
        query = insert_dict[key][1]
        schema = insert_dict[key][2]
        needs_join = insert_dict[key][3]
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
            # This is from the staging database.
            if 'wet' in query or 'water_licences' in query:
                from_conn = get_wet_conn()
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)

            # This is from the destination database. Sometimes there has to be a join or some manipulation of the data that already exist in there.
            elif "bcwat" in query:
                from_conn = to_conn
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)

            # This will be the old dev, or prod database, depending on which one is in the .env file.
            else:
                from_conn = get_from_conn()
                from_cur = from_conn.cursor(cursor_factory = RealDictCursor)

            logger.debug(f"Getting data from the table query")
            from_cur.execute(query)
            records = pd.DataFrame(from_cur.fetchmany(1000000))

            # Make sure that unneeded cimate variables don't make it to the database.
            if key == "climate_station_variable":
                logger.debug(f"{key} detected, this requires some conversions")
                records = records.replace({"variable_id": climate_var_id_conversion})
                records = records.loc[records["variable_id"] <= 29, : ]

            # Make sure that unneeded water variables don't make it in to the database
            if key == "water_station_variable":
                logger.debug(f"Removing variables not used in prod for {key}")
                records = records.loc[records["variable_id"] <= 3, : ]

            # Since the climate and water variables are in different tables in the original scrapers
            # and the new scraper has the variable id's in the same table, we have to do some conversions
            if key == "variables":
                records = special_variable_function(records)

            # This is for the bcwat destination table. To populate the station metadata tables with the correct
            # station_ids, the new station_ids from the destination database must be joined on.
            if 'bcwat' not in query and needs_join == "join":
                logger.debug(f"Getting station_id from destination table")
                to_cur.execute(f"SELECT original_id, station_id FROM bcwat_obs.station")
                station = pd.DataFrame(to_cur.fetchall())
                logger.debug(f"Joining the two tables together.")

                records = station.merge(records, on="original_id", how="inner").drop("original_id", axis=1)

            while len(records) != 0:
                records.replace({np.nan:None}, inplace=True)
                # JSON and BJSON objects from postgres are read as strings. Applying json.dumps allows them to be inserted as
                # JSON Objects. 114 is JSON, 3802 is BJSON
                for col_types in from_cur.description:
                    if col_types[1] in [114, 3802]:
                        records[col_types[0]] = records[col_types[0]].apply(json.dumps)
                columns = records.columns.to_list()
                insert_tuple = records.to_records(index=False).tolist()

                insert_query =f'''INSERT INTO {schema}.{table}({','.join(columns)}) VALUES %s'''

                logger.debug(f"Inserting large table {table} into {schema}.{table}")

                execute_values(to_cur, insert_query, insert_tuple)

                # Fetch more records if 1 000 000 did not read all the records.
                records = pd.DataFrame(from_cur.fetchmany(1000000))

        except Exception as e:
            logger.error(f"Something went wrong inserting the large tables!", exc_info=True)
            to_conn.rollback()
            to_conn.close()
            from_conn.rollback()
            from_conn.close()
            raise RuntimeError

        to_conn.commit()

def run_post_import_queries(to_conn):
    """
    Runs the post_import_query after all the data has been imported. Very simple.

    Args:
        to_conn (psycopg2.extensions.connection): The connection to the destination database.
    """
    cursor = to_conn.cursor()

    cursor.execute(post_import_query)

    to_conn.commit()

    cursor.close()

def import_non_scraped_data():
    logger.debug("Connecting to To database")
    to_conn = get_to_conn()

    logger.debug("Importing tables in the bcwat_obs_data dictionary")
    # populate_all_tables(to_conn, bcwat_obs_data)

    logger.debug("Importing tables in the bcwat_licence_data dictionary")
    populate_all_tables(to_conn, bcwat_licence_data)

    logger.debug("Running post import queries")
    run_post_import_queries(to_conn)

    to_conn.close()
