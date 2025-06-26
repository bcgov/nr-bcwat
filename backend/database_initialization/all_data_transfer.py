from util import (
    get_from_conn,
    get_to_conn,
    get_wet_conn,
    special_variable_function,
)
from constants import (
    bcwat_obs_data,
    bcwat_licence_data,
    bcwat_watershed_data,
    logger,
    climate_var_id_conversion
)
from queries.post_import_queries import post_import_query
from psycopg2.extras import execute_values, RealDictCursor
from psycopg2.extensions import AsIs, register_adapter
import psycopg2 as pg2
import pandas as pd
import numpy as np
import json
from io import StringIO
import os

register_adapter(np.int64, AsIs)

def populate_all_tables(insert_dict):
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

    for key in insert_dict.keys():

        to_conn = get_to_conn()
        to_cur = to_conn.cursor(cursor_factory = RealDictCursor)
        # Read all dictionary values and assign them to variables
        table = insert_dict[key][0]
        query = insert_dict[key][1]
        schema = insert_dict[key][2]
        needs_join = insert_dict[key][3]

        if schema == "bcwat_ws":
            if table == "fund_rollup_report":
                fetch_batch = 25000
            elif table == "ws_geom_all_report":
                fetch_batch = 15000
            else:
                fetch_batch= 100000
        else:
            fetch_batch = 200000

        try:
            logger.debug("Truncating Destination Table before insert")
            to_cur.execute(f"TRUNCATE TABLE {schema}.{table} CASCADE;")
        except Exception as e:
            logger.error(f"Something went wrong truncating the destination table!", exc_info=True)
            to_conn.rollback()
            to_conn.close()
            from_conn.rollback()
            from_conn.close()
            raise RuntimeError

        try:
            # This is from the staging database, it's wet. because without the . it would detect wetland as well.
            if 'wet.' in query or 'water_licences' in query:
                logger.info("Setting from connection and cursor to be database with schema wet")
                from_conn = get_wet_conn()
                from_cur = from_conn.cursor(name='wet_cur', cursor_factory = RealDictCursor)
                from_cur.itersize = fetch_batch

            # This is from the destination database. Sometimes there has to be a join or some manipulation of the data that already exist in there.
            elif "bcwat" in query:
                logger.info("Setting from connection and cursor to be database with schema bcwat")
                from_conn = get_to_conn()
                from_cur = from_conn.cursor(name='bcwat_cur', cursor_factory = RealDictCursor)
                from_cur.itersize = fetch_batch

            # This will be the old dev, or prod database, depending on which one is in the .env file.
            else:
                logger.info("Setting from connection and cursor to be database with schema cariboo, owt, nwwt, kwt, water, and bcwmd")
                from_conn = get_from_conn()
                from_cur = from_conn.cursor(name='bcwt_cur', cursor_factory = RealDictCursor)
                from_cur.itersize = fetch_batch

            logger.debug(f"Getting data from the table query")
            from_cur.execute(query)
            records = pd.DataFrame(from_cur.fetchmany(fetch_batch))

            # Make sure that unneeded cimate variables don't make it to the database.
            if key == "climate_station_variable":
                logger.debug(f"{key} detected, this requires some conversions")
                records = records.loc[records["variable_id"] <= 29, : ]

            # Make sure that unneeded water variables don't make it in to the database
            if key == "water_station_variable":
                logger.debug(f"Removing variables not used in prod for {key}")
                records = records.loc[records["variable_id"] <= 3, : ]

            # Since the climate and water variables are in different tables in the original scrapers
            # and the new scraper has the variable id's in the same table, we have to do some conversions
            if key == "variables":
                records = special_variable_function(records)

            # If the station_id is in the query then it needs to be joined to the new station_id. So gather the new station_id, along with
            # original_id, lat, lon, to join on.
            if 'bcwat' not in query and needs_join == "join":
                logger.debug(f"Getting station_id from destination table")
                to_cur.execute(f"SELECT original_id, station_id, longitude, latitude FROM bcwat_obs.station")
                station = pd.DataFrame(to_cur.fetchall())

            num_inserted_rows = 0

            while len(records) != 0:
                # This is for the bcwat destination table. To populate the station metadata tables with the correct
                # station_ids, the new station_ids from the destination database must be joined on.
                if 'bcwat' not in query and needs_join == "join":
                    logger.debug(f"Joining the two tables together.")
                    records = station.merge(records, on=["original_id", "longitude", "latitude"], how="inner").drop(columns=["original_id", "longitude", "latitude"], axis=1)

                # Replace all nan values with None
                records.replace({np.nan:None}, inplace=True)

                # If the variables are climate variables then they need to be transfromed according to the changes that were made in the new
                # scraper.
                if ("climate" in key):
                    records = records.replace({"variable_id": climate_var_id_conversion})

                # JSON and BJSON objects from postgres are read as strings. Applying json.dumps allows them to be inserted as
                # JSON Objects. 114 is JSON, 3802 is BJSON
                for col_types in from_cur.description:
                    if col_types[1] in [114, 3802]:
                        records[col_types[0]] = records[col_types[0]].apply(json.dumps)

                # There are some lists or JSON objects in the columns that cannot be hashed
                if schema == 'bcwat_obs':
                    records.drop_duplicates(inplace=True)

                columns = ', '.join(records.columns.to_list())
                rows = [tuple(x) for x in records.to_numpy()]

                logger.debug(f"Inserting large table {table} into {schema}.{table}")

                insert_query = f"INSERT INTO {schema}.{table} ({columns}) VALUES %s ON CONFLICT ON CONSTRAINT {table}_pkey DO NOTHING;"
                execute_values(to_cur, insert_query, rows)

                # Fetch more records if fetch_batch did not read all the records.
                num_inserted_rows += len(records)
                logger.info(f"Inserted a total of {num_inserted_rows} rows, fetching more if there are more.")

                records = pd.DataFrame(from_cur.fetchmany(fetch_batch))

            to_conn.commit()

        except Exception as e:
            logger.error(f"Something went wrong inserting the large tables!", exc_info=True)
            to_conn.rollback()
            from_conn.rollback()
            raise RuntimeError(f"Something went wrong inserting the large tables!")
        finally:
            to_cur.close()
            from_cur.close()
            to_conn.close()
            from_conn.close()


def run_post_import_queries():
    """
    Runs the post_import_query after all the data has been imported. Very simple.

    Args:
        to_conn (psycopg2.extensions.connection): The connection to the destination database.
    """
    to_conn = get_to_conn()

    cursor = to_conn.cursor()

    cursor.execute(post_import_query)

    to_conn.commit()

    cursor.close()

    to_conn.close()

def import_non_scraped_data():
    logger.debug("Connecting to To database")

    logger.debug("Importing tables in the bcwat_obs_data dictionary")
    populate_all_tables(bcwat_obs_data)

    logger.debug("Importing tables in the bcwat_licence_data dictionary")
    populate_all_tables(bcwat_licence_data)

    logger.debug("Importing tables in the bcwat_watershed_data dictionary")
    populate_all_tables(bcwat_watershed_data)

    logger.debug("Running post import queries")
    run_post_import_queries()
