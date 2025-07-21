from util import (
    get_from_conn,
    get_to_conn,
    get_wet_conn,
    special_variable_function,
    create_partions,
    send_file_to_s3,
    open_file_in_s3,
    make_table_from_to_db,
    determine_file_size_s3,
    construct_insert_tables,
    insert_new_stations
)
from constants import (
    bcwat_obs_data,
    bcwat_licence_data,
    bcwat_watershed_data,
    other_needed_data,
    logger,
    climate_var_id_conversion,
    data_import_dict_from_s3,
    geom_column_names4326,
    geom_column_names3005,
    climate_var_tables
)
from queries.bcwat_obs_data import nwp_stations_query
from queries.bcwat_watershed_data import wsc_station_query
from queries.post_import_queries import post_import_query
from psycopg2.extras import execute_values, RealDictCursor
from psycopg2.extensions import AsIs, register_adapter
import psycopg2 as pg2
import pandas as pd
import numpy as np
import polars as pl
import polars_st as st
import polars.selectors as cs
import json
import os
import pathlib


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
    total_rows_inserted = 0

    for key in insert_dict.keys():

        logger.info(f"\n\nSTARTING INSERT FOR {key}\n")

        to_conn = get_to_conn()
        to_cur = to_conn.cursor(cursor_factory = RealDictCursor)
        # Read all dictionary values and assign them to variables
        table = insert_dict[key][0]
        query = insert_dict[key][1]
        schema = insert_dict[key][2]
        needs_join = insert_dict[key][3]

        if schema == "bcwat_ws":
            if table == "fund_rollup_report":
                fetch_batch = 2500
            elif table == "ws_geom_all_report":
                fetch_batch = 2500
            else:
                fetch_batch= 2500
        else:
            fetch_batch = 100000

        try:
            if table != "station_observation":
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
            if 'wet.' in query or 'water_licences' in query or 'public.' in query:
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

            logger.debug(f"Getting data from the table {key}")
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
                to_cur.execute(f"SELECT station_id, old_station_id FROM bcwat_obs.station")
                station = pd.DataFrame(to_cur.fetchall())
                if key == "fdc_wsc_station_in_model":
                    wet_conn = get_wet_conn()
                    wet_cur = wet_conn.cursor(cursor_factory=RealDictCursor)
                    wet_cur.execute(wsc_station_query)
                    wsc_stations = pd.DataFrame(wet_cur.fetchall())
                    wet_cur.close()
                    wet_conn.close()
                elif key in ["extreme_flow", "nwp_flow_metric"]:
                    wet_conn = get_wet_conn()
                    wet_cur = wet_conn.cursor(cursor_factory=RealDictCursor)
                    wet_cur.execute(nwp_stations_query)
                    nwp_stations = pd.DataFrame(wet_cur.fetchall())
                    wet_cur.close()
                    wet_conn.close()

            num_inserted_rows = 0

            while len(records) != 0:
                # This is for the bcwat destination table. To populate the station metadata tables with the correct
                # station_ids, the new station_ids from the destination database must be joined on.
                if 'bcwat' not in query and needs_join == "join":
                    logger.debug(f"Joining the two tables together.")

                    if key in ["extreme_flow", "nwp_flow_metric"]:
                        records = nwp_stations.merge(records, on=["original_id"], how="inner").drop(columns=["original_id"], axis=1)
                    elif key == "fdc_wsc_station_in_model":
                        records = wsc_stations.merge(records, on=["original_id"], how="inner")

                    records = station.merge(records, on=["old_station_id"], how="inner").drop(columns=["old_station_id"], axis=1)

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
                total_rows_inserted += len(records)

                logger.info(f"Inserted a total of {num_inserted_rows} rows into the table {table}, and a total of {total_rows_inserted} rows into the schema {schema}.")

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

        if table == "station":
            logger.debug("Creating partitions")
            create_partions()

    return total_rows_inserted

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

def import_data():
    """
    Function that calls the controls the whole import
    """
    logger.debug("Connecting to To database")
    num_rows = 0

    logger.debug("Importing tables in the bcwat_obs_data dictionary")
    num_rows += populate_all_tables(bcwat_obs_data)
    logger.info(f"Inserted a total of {num_rows} rows into the database")

    logger.debug("Importing tables in the bcwat_licence_data dictionary")
    num_rows += populate_all_tables(bcwat_licence_data)
    logger.info(f"Inserted a total of {num_rows} rows into the database")

    logger.debug("Importing tables in the bcwat_watershed_data dictionary")
    num_rows += populate_all_tables(bcwat_watershed_data)
    logger.info(f"Inserted a total of {num_rows} rows into the database")

    logger.debug("Running post import queries")
    run_post_import_queries()

def create_csv_files():
    """
    Creates CSV files for each table in the data dictionaries
    and then uploads them to the s3 bucket

    The function loops through each of the data dictionaries and
    for each table, it creates a CSV file for the table and uploads
    it to the s3 bucket.

    The function also uses the send_file_to_s3 function to upload
    the CSV files to the s3 bucket.

    The function will also remove the uncompressed CSV file after
    it has been uploaded to the s3 bucket.

    If there is an error at any point in the function, it will
    raise a RuntimeError with the error message.
    """
    logger.info("Getting absolute path to where the data will be saved")
    abs_path = pathlib.Path(__file__).parent.resolve()
    temp_dir = os.path.join(abs_path, "temp")

    for data_dict in [bcwat_obs_data, bcwat_licence_data, bcwat_watershed_data, other_needed_data]:
        for key in data_dict.keys():
            if key == "station_region":
                logger.info(f"The table {key} can be generated post script. So we will be ignoring this one for now.")
                continue

            logger.info(f"Starting transformation for {key}")
            table = key
            query = data_dict[key][1]

            try:
                if 'wet.' in query or 'water_licences' in query or "public." in query:
                    logger.info("Setting from connection and cursor to be database with schema wet")
                    from_conn = get_wet_conn()
                    from_cur = from_conn.cursor()
                else:
                    logger.info("Setting from connection and cursor to be database with schema cariboo, owt, nwwt, kwt, water, and bcwmd")
                    from_conn = get_from_conn()
                    from_cur = from_conn.cursor()
            except Exception as e:
                logger.error(f"Failed to get the cursor for the right connection!", exc_info=True)
                raise RuntimeError(f"Failed to get the cursor for the right connection! Error: {e}")

            try:
                logger.debug(f"Writing CSV file for {table}")
                with open(f"{temp_dir}/{table}.csv", "wb") as f:
                    query = f"""
                        COPY ({query}) TO STDOUT WITH (FORMAT 'csv', DELIMITER ',', HEADER, NULL 'None');
                    """
                    from_cur.copy_expert(sql=query, file=f)
            except Exception as e:
                logger.error(f"Something went wrong when running the query create a csv! {e}", exc_info=True)
                raise RuntimeError(f"Something went wrong when running the query create a csv! {e}")

            try:
                send_file_to_s3(path_to_file=f"{temp_dir}/{table}.csv")
            except Exception as e:
                logger.error(f"Failed to upload file to s3 bucket! Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed to upload file to s3 bucket! Error: {e}")

            try:
                logger.debug(f"Removing uncompressed CSV as well as compressed CSV for {table}")
                os.remove(f"{temp_dir}/{table}.csv")
            except Exception as e:
                logger.error(f"Failed to delete file {temp_dir}/{table}.csv from the file system! Error: {e}", exc_info=True)
                raise RuntimeError(f"Failed to delete file {temp_dir}/{table}.csv from the file system! Error: {e}")

def import_from_s3():
    """
    This function imports the data from the S3 bucket, and populates the destination database.
    the files will be imported from the S3 bucket without downloading the whole file. It will insert it into the corresponding table in the destination database.
    The function will also run the post import queries after all of the data has been inserted.
    If there is an error at any point in the function, it will raise a RuntimeError with the error message.
    """

    logger.info(f"Importing database files from S3 then populating database.")
    abs_path = pathlib.Path(__file__).parent.resolve()
    temp_dir = os.path.join(abs_path, "temp")
    total_inserted = 0

    for filename in data_import_dict_from_s3.keys():
        table = data_import_dict_from_s3[filename]["tablename"]
        schema = data_import_dict_from_s3[filename]["schema"]
        needs_join = data_import_dict_from_s3[filename]["needs_join"]
        table_dtype = data_import_dict_from_s3[filename]["dtype"]
        chunk_start = 0
        chunk_size = 75000000
        chunk_end = chunk_start + chunk_size - 1

        if filename == "station_region":
            total_inserted += make_table_from_to_db(table=table, query=bcwat_obs_data[filename][1], schema=schema, dtype=table_dtype)
            continue

        file_size = determine_file_size_s3(filename)
        logger.info(f"file size = {file_size}")

        logger.info(f"Importing file {filename} into database")

        try:
            logger.debug(f"Getting database connection to insert to")
            to_conn = get_to_conn()
            to_cur = to_conn.cursor(cursor_factory=RealDictCursor)
        except Exception as e:
            logger.error(f"Failed to get connection and create cursor for the destination database. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to get connection and create cursor for the destination database. Error: {e}")

        try:
            if table != "station_observation":
                logger.debug("Truncating Destination Table before insert")
                to_cur.execute(f"TRUNCATE TABLE {schema}.{table} CASCADE;")
        except Exception as e:
            logger.error(f"Something went wrong truncating the destination table!", exc_info=True)
            to_conn.rollback()
            to_conn.close()
            raise RuntimeError

        logger.info(f"Reading file {filename}.csv in chunks of {chunk_size} bytes")
        try:
            logger.debug(f"Reading CSV file {filename}.csv in chunks")

            # If the station_id is in the query then it needs to be joined to the new station_id. So gather the new station_id, along with
            # original_id, lat, lon, to join on.
            if needs_join:
                logger.debug(f"Getting new station_ids for {filename}")
                station = pl.read_database(
                    query = "SELECT station_id, old_station_id FROM bcwat_obs.station",
                    connection = to_conn,
                    infer_schema_length=None
                ).lazy()
                if filename in ["extreme_flow", "nwp_flow_metric"]:
                    nwp_size = determine_file_size_s3(file_name="nwp_stations")
                    nwp_data, nwp_start, nwp_end = open_file_in_s3(file_name="nwp_stations", chunk_size=chunk_size, object_size=nwp_size, chunk_start=0, chunk_end=nwp_size)
                    nwp_station = pl.scan_csv(nwp_data, has_header=True, infer_schema=True, infer_schema_length=None, null_values=["None"])
                    del nwp_start, nwp_end
                elif filename == "fdc_wsc_station_in_model":
                    wsc_size = determine_file_size_s3(file_name="wsc_station")
                    wsc_data, wsc_start, wsc_end = open_file_in_s3(file_name="wsc_station", chunk_size=chunk_size, object_size=wsc_size, chunk_start=0, chunk_end=wsc_size)
                    wsc_station = pl.scan_csv(wsc_data, has_header=True, infer_schema=True, infer_schema_length=None, null_values=["None"])
                    del wsc_start, wsc_end

            num_inserted_to_table = 0
            partial_batch = b""
            newline = "\n".encode()
            header = []

            while chunk_start <= file_size:
                logger.info(f"Start_chunk {chunk_start}")
                logger.info(f"End_chunk {chunk_end}")
                batch, chunk_start, chunk_end = open_file_in_s3(file_name=filename, chunk_size=chunk_size, object_size=file_size, chunk_start=chunk_start, chunk_end=chunk_end)

                batch = batch.replace(b"\n          ", b"")

                if num_inserted_to_table == 0:
                    first_new_line = batch.find(newline)
                    header = batch[:first_new_line+1].decode().strip("\n").split(",")
                    batch = batch[first_new_line+1:]

                batch = partial_batch + batch

                last_newline = batch.rfind(newline)

                # keep the partial line you've read here
                partial_batch = batch[last_newline+1:]
                # write to a smaller file, or work against some piece of data
                batch = batch[0:last_newline+1]

                logger.info(f"insert bytes = {len(batch)}")

                batch = pl.scan_csv(batch, has_header=False, new_columns=header, schema_overrides=table_dtype, null_values=["None"])

                # Make sure that unneeded cimate variables don't make it to the database.
                if filename == "climate_station_variable":
                    logger.debug(f"{filename} detected, this requires some minor adjustments")
                    batch = batch.filter(pl.col("variable_id") <= 29)

                # Make sure that unneeded water variables don't make it in to the database
                if filename == "water_station_variable":
                    logger.debug(f"{filename} detected, this requires some minor adjustments")
                    batch = batch.filter(pl.col("variable_id") <= 3)

                if filename in climate_var_tables:
                    batch = (
                        batch
                        .with_columns(
                            variable_id = pl.col("variable_id").replace_strict(climate_var_id_conversion, default=pl.col("variable_id"))
                        )
                    )
                # Since the climate and water variables are in different tables in the original scrapers
                # and the new scraper has the variable id's in the same table, we have to do some conversions
                if filename == "variable":
                    batch = special_variable_function(batch, polars=True)

                # This is for the bcwat destination table. To populate the station metadata tables with the correct
                # station_ids, the new station_ids from the destination database must be joined on.
                if needs_join:
                    if filename in ["extreme_flow", "nwp_flow_metric"]:
                        batch = nwp_station.join(batch, on="original_id", how="inner").drop("original_id")
                    elif filename == "fdc_wsc_station_in_model":
                        batch = wsc_station.join(batch, on="original_id", how="inner")

                    batch = station.join(batch, on="old_station_id", how="inner").drop("old_station_id")

                if (schema == "bcwat_obs") and (filename != "variable"):
                    batch = batch.unique()

                batch = (
                    batch
                    .with_columns(
                        st.from_geojson(cs.by_name(geom_column_names4326, require_all=False)).st.set_srid(4326),
                        st.from_geojson(cs.by_name(geom_column_names3005, require_all=False)).st.set_srid(3005)
                    )
                ).collect()

                rows = batch.rows()
                columns = ", ".join(batch.columns)

                logger.info(f"Inserting {len(rows)} rows into the table {schema}.{table}")

                query = f"INSERT INTO {schema}.{table}({columns}) VALUES %s ON CONFLICT ON CONSTRAINT {table}_pkey DO NOTHING;"

                execute_values(cur=to_cur, sql=query, argslist=rows, page_size=100000)

                num_inserted_to_table += len(rows)
                total_inserted += len(rows)

                to_conn.commit()

        except StopIteration as e:
            logger.info(f"Finished inserting data in to the database for {filename}")
        except Exception as e:
            to_conn.rollback()
            logger.error(f"Failed to import file {filename} to the table {schema}.{table}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Failed to import file {filename} to the table {schema}.{table}. Error: {e}")
        finally:
            to_cur.close()
            to_conn.close()

        logger.info(f"Inserted {num_inserted_to_table} to the table {table}")
        logger.info(f"Inserted {total_inserted} to the database so far")

        if filename == "station":
            logger.debug("Creating partitions")
            create_partions()

    logger.info("Finished inserting data, running post insert queries")
    run_post_import_queries()

def insert_missing_stations():
    """
    Function that will insert all the new stations as of July 17th 2025 that are not in the database. This is only done for the scrapers
    that do not have an automatic function to add stations in the database.

    The functions that are called, `construct_insert_tables`, and `insert_new_stations` are taken directly from the [`StationObservationPipeline`](../../airflow/etl_pipelines/scrapers/StationObservationPipeline/StationObservationPipeline.py) class.
    """
    logger.info("Inserting missing stations")
    to_conn = get_to_conn()
    abs_path = pathlib.Path(__file__).parent.resolve()

    data = (
        pl.scan_csv(
        os.path.join(abs_path,"new_stations.csv"),
        null_values=["None"],
        schema_overrides={
            "original_id":pl.String,
            "station_name":pl.String,
            "longitude":pl.Float64,
            "latitude":pl.Float64,
            "elevation":pl.Float64,
            "stream_name":pl.String,
            "station_description":pl.String,
            "scrape": pl.Boolean,
            "station_status_id": pl.Int64,
            "operation_id":pl.Int64,
            "drainage_area":pl.Float64,
            "regulated":pl.Boolean,
            "user_flag":pl.Boolean,
            "year":pl.String,
            "project_id":pl.String,
            "network_id":pl.Int64,
            "type_id":pl.Int64,
            "variable_id":pl.String
        }
        )
        .with_columns(
            pl.col("project_id").cast(pl.List(pl.Int16)),
            pl.col("year").cast(pl.List(pl.Int64)),
            pl.col("variable_id").str.split(",").cast(pl.List(pl.Int64))
        )
    )

    try:
        new_stations, station_metadata = construct_insert_tables(data)

        insert_new_stations(new_stations, station_metadata, to_conn)
    except Exception as e:
        logger.error(f"Failed to construct metadata dict or insert new station data! Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to construct metadata dict or insert new station data! Error: {e}")
    finally:
        to_conn.close()

    to_conn.close()
    logger.info("Finished Inserting New stations.")
