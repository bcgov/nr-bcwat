from dotenv import load_dotenv, find_dotenv
from psycopg2.extras import execute_values
from constants import (
    logger,
    NEW_STATION_INSERT_DICT_TEMPLATE
)
import logging
import os
import boto3
from botocore.client import Config
import psycopg2 as pg2
import polars as pl
import pathlib
import smart_open

load_dotenv(find_dotenv())

## From DB params
fromhost = os.getenv("FROMHOST")
fromuser = os.getenv("FROMUSER")
fromport = os.getenv("FROMPORT")
frompass = os.getenv("FROMPASS")
fromdb = os.getenv("FROMDB")

## To DB params
tohost = os.getenv("TOHOST")
touser = os.getenv("TOUSER")
toport = os.getenv("TOPORT")
topass = os.getenv("TOPASS")
todb = os.getenv("TODB")

## DB with wet Schema
wethost = os.getenv("WETHOST")
wetuser = os.getenv("WETUSER")
wetport = os.getenv("WETPORT")
wetpass = os.getenv("WETPASS")
wetdb = os.getenv("WETDB")

def setup_logging():
    """
    Function to set up the logging module.
    """
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(pathname)s - %(funcName)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def get_from_conn():
    """
    Get a connection to the database specified in the environment variables.
    This connection is used to read data from the source database.
    """
    ssl = 'require'
    if fromdb == 'ogc':
        ssl = 'disable'
    return pg2.connect(
        host=fromhost,
        port=fromport,
        user=fromuser,
        password=frompass,
        dbname=fromdb,
        sslmode=ssl,
        keepalives=1,
        keepalives_idle=20,
        keepalives_interval=10,
        keepalives_count=5
    )

def get_to_conn():
    """
    Get a connection to the database specified in the environment variables.
    This connection is used to write data to the destination database.
    """

    return pg2.connect(
        host=tohost,
        port=toport,
        user=touser,
        password=topass,
        dbname=todb,
        sslmode='require',
        keepalives=1,
        keepalives_idle=20,
        keepalives_interval=10,
        keepalives_count=5
    )

def get_wet_conn():
    """
    Get a connection to the database specified in the environment variables.
    This connection is used to read data from the database with the wet schema.
    """
    return pg2.connect(
        host=wethost,
        port=wetport,
        user=wetuser,
        password=wetpass,
        dbname=wetdb,
        sslmode='require',
        keepalives=1,
        keepalives_idle=20,
        keepalives_interval=10,
        keepalives_count=5
    )


def recreate_db_schemas():
    """
    Drop any partitions that exist in the database.
    Drop the schemas: bcwat_obs, bcwat_ws, and bcwat_lic then recreate them from their respective ERD diagrams.

    This function is used to ensure that the schemas are in the correct state before importing data. This is
    useful in situations where the database is being built for the first time, or when changes are being made
    to the database schema.

    """
    from queries.bcwat_watershed_erd_diagram import bcwat_ws_query
    from queries.bcwat_obs_erd_diagram import bcwat_obs_query
    from queries.bcwat_licence_erd_diagram import bcwat_lic_query

    to_conn = get_to_conn()
    cur = to_conn.cursor()

    logger.debug("Creating PostGIS extension")
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
        to_conn.commit()
    except Exception as e:
        logger.error(f"Failed to create PostGIS extension. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to create PostGIS extension. Error: {e}")

    logger.debug("Dropping all Partitions")
    delete_partions()

    drop_query = '''
        DROP SCHEMA IF EXISTS bcwat_obs CASCADE;
        DROP SCHEMA IF EXISTS bcwat_ws CASCADE;
        DROP SCHEMA IF EXISTS bcwat_lic CASCADE;
    '''

    try:
        logger.debug(f"Drop Cascading Schemas: bcwat_obs, bcwat_ws, bcwat_lic")
        cur.execute(drop_query)
        to_conn.commit()
    except Exception as e:
        logger.error(f"There was an issue drop cascading the schemas bcwat_obs, bcwat_ws, and bcwat_lic!", exc_info=True)
        to_conn.rollback()
        to_conn.close()
        raise RuntimeError


    try:
        logger.debug(f"Repopulating the Previously dropped schemas")
        logger.debug(f"Starting with bcwat_obs")
        cur.execute(bcwat_obs_query)
        logger.debug(f"Next bcwat_ws")
        cur.execute(bcwat_ws_query)
        logger.debug(f"Lastly bcwat_lic")
        cur.execute(bcwat_lic_query)
        to_conn.commit()
        logger.debug("Done")
    except Exception as e:
        logger.error(f"There was an issue repopulating the schemas!", exc_info=True)
        to_conn.rollback()
        to_conn.close()
        raise RuntimeError(e)

def special_variable_function(df, polars=False):
    """
    A function to special case certain variables in the variables table.

    Some variables need their ids and/or names changed in order to be consistent with the climate variables.
    This function takes a dataframe and changes the ids and names of the variables as needed.
    """
    if not polars:
        df.iloc[27, 0] = 25
        df.iloc[28, 0] = 26
        df.iloc[0, 0] = 27
        df.iloc[2, 0] = 28
        df.iloc[5, 0] = 29

        df.iloc[20, 1] = "msp_sd"
        df.iloc[21, 1] = "msp_water_equivalent"
        df.iloc[22, 1] = "msp_percent_normal"
        df.iloc[23, 1] = "msp_percent_density"
        df.iloc[24, 1] = "msp_normal"
        df.iloc[25, 1] = "rh"
        df.iloc[26, 1] = "psc"
        df.iloc[27, 1] = "dewpoint"
        df.iloc[28, 1] = "uv_index"

        df.iloc[11, 2] = "Average Wind Speed"
        df.iloc[12, 2] = "Maximum Wind Speed"
        df.iloc[13, 2] = "Wind Direction"
        df.iloc[14, 2] = "Road Temperature"
        df.iloc[15, 2] = "Snow Accumulation since 0600 or 1800"
        df.iloc[16, 2] = "Snow Accumulation in the past 12 hours ending at 0600 or 1800"
        df.iloc[17, 2] = "Total Precipitation in the last 1hr"
        df.iloc[19, 2] = "Precipitation Accumulation Since 0600 or 1800"
        df.iloc[20, 2] = "Manual Snow Pillow Snow Depth"
        df.iloc[21, 2] = "Manual Snow Pillow Water Equivalent"
        df.iloc[22, 2] = "Manual Snow Pillow Percent of Normal"
        df.iloc[23, 2] = "Manual Snow Pillow Percent of Density"
        df.iloc[24, 2] = "Manual Snow Pillow Normal"
        df.iloc[25, 2] = "Relative Humidity"
        df.iloc[27, 2] = "Dewpoint"
        df.iloc[28, 2] = "Ultra Violet Index"

        df.sort_values(by="variable_id", inplace=True)
    else:
        df = (
            df
            .with_columns(
                variable_id = (pl
                    .when(pl.col("variable_id") == 26).then(25)
                    .when(pl.col("variable_id" ) == 25).then(26)
                    .when((pl.col("variable_id") == 1) & (pl.col("variable_name") == pl.lit("lwe_thickness_of_precipitation_amount"))).then(27)
                    .when((pl.col("variable_id") == 2) & (pl.col("variable_name") == pl.lit("lwe_thickness_of_precipitation"))).then(28)
                    .when((pl.col("variable_id") == 3) & (pl.col("variable_name") == pl.lit("thickness_of_rainfall_amount"))).then(29)
                    .otherwise(pl.col("variable_id"))
                )
            )
            .with_columns(
                variable_name = (pl
                    .when(pl.col("variable_id") == 18).then(pl.lit("msp_sd"))
                    .when(pl.col("variable_id") == 19).then(pl.lit("msp_water_equivalent"))
                    .when(pl.col("variable_id") == 20).then(pl.lit("msp_percent_normal"))
                    .when(pl.col("variable_id") == 21).then(pl.lit("msp_percent_density"))
                    .when(pl.col("variable_id") == 22).then(pl.lit("msp_normal"))
                    .when(pl.col("variable_id") == 23).then(pl.lit("rh"))
                    .when(pl.col("variable_id") == 24).then(pl.lit("psc"))
                    .when(pl.col("variable_id") == 25).then(pl.lit("dewpoint"))
                    .when(pl.col("variable_id") == 26).then(pl.lit("uv_index"))
                    .otherwise(pl.col("variable_name"))
                ),
                variable_description = (pl
                    .when(pl.col("variable_id") == 9).then(pl.lit("Average Wind Speed"))
                    .when(pl.col("variable_id") == 10).then(pl.lit("Maximum Wind Speed"))
                    .when(pl.col("variable_id") == 11).then(pl.lit("Wind Direction"))
                    .when(pl.col("variable_id") == 12).then(pl.lit("Road Temperature"))
                    .when(pl.col("variable_id") == 13).then(pl.lit("Snow Accumulation since 0600 or 1800"))
                    .when(pl.col("variable_id") == 14).then(pl.lit("Snow Accumulation in the past 12 hours ending at 0600 or 1800"))
                    .when(pl.col("variable_id") == 15).then(pl.lit("Total Precipitation in the last 1hr"))
                    .when(pl.col("variable_id") == 17).then(pl.lit("Precipitation Accumulation Since 0600 or 1800"))
                    .when(pl.col("variable_id") == 18).then(pl.lit("Manual Snow Pillow Snow Depth"))
                    .when(pl.col("variable_id") == 19).then(pl.lit("Manual Snow Pillow Water Equivalent"))
                    .when(pl.col("variable_id") == 20).then(pl.lit("Manual Snow Pillow Percent of Normal"))
                    .when(pl.col("variable_id") == 21).then(pl.lit("Manual Snow Pillow Percent of Density"))
                    .when(pl.col("variable_id") == 22).then(pl.lit("Manual Snow Pillow Normal"))
                    .when(pl.col("variable_id") == 23).then(pl.lit("Relative Humidity"))
                    .when(pl.col("variable_id") == 25).then(pl.lit("Dewpoint"))
                    .when(pl.col("variable_id") == 26).then(pl.lit("Ultra Violet Index"))
                )
            )
            .sort(by="variable_id")
        )

    return df

def create_partions():
    """
    Create partitions for the tables: station_observation and water_quality_hourly.

    There are 25 partitions for each table, each of which is created with the
    remainder of a modulus operation. The modulus used is 25, and the remainder
    is the value of the row in the partition table (0-24).
    """
    to_conn = get_to_conn()
    cursor = to_conn.cursor()
    try:
        for row in range(25):
            query = f"""
                CREATE TABLE bcwat_obs.station_observation_{row} PARTITION OF bcwat_obs.station_observation FOR VALUES WITH (MODULUS 25, REMAINDER {row});
                CREATE TABLE bcwat_obs.water_quality_hourly_{row} PARTITION OF bcwat_obs.water_quality_hourly FOR VALUES WITH (MODULUS 25, REMAINDER {row});
            """
            cursor.execute(query)
    except Exception as e:
        logger.error("Failed to make partitions for station_observation table", exc_info=True)
        to_conn.rollback()
        cursor.close()
        to_conn.close()
        raise RuntimeError

    to_conn.commit()
    cursor.close()
    to_conn.close()

def delete_partions():
    """
    Deletes all partitions for the tables: station_observation and water_quality_hourly.
    """

    to_conn = get_to_conn()
    cursor = to_conn.cursor()

    query = """
        SELECT
            child.relname AS child
        FROM pg_inherits
        JOIN
            pg_class parent
        ON
            pg_inherits.inhparent = parent.oid
        JOIN
            pg_class child
        ON
            pg_inherits.inhrelid   = child.oid
        JOIN
            pg_namespace nmsp_parent
        ON
            nmsp_parent.oid  = parent.relnamespace
        JOIN
            pg_namespace nmsp_child
        ON
            nmsp_child.oid   = child.relnamespace
        WHERE
            parent.relname='station_observation'
        OR
            parent.relname='water_quality_hourly';
    """
    try:
        df = pl.read_database(query=query, connection=to_conn)

        for row in df.iter_rows():
            delete_query = f"""
                DROP TABLE IF EXISTS bcwat_obs.{row[0]};
            """
            cursor.execute(delete_query)
            to_conn.commit()
    except Exception as e:
        to_conn.rollback()
        cursor.close()
        to_conn.close()
        logger.error(f"Failed dropping partitions for station_observation table", exc_info=True)
        raise RuntimeError(f"Failed dropping partitions for station_observation table")

    cursor.close()
    to_conn.close()

def send_file_to_s3(path_to_file):
    """
    Sends a CSV file to S3 Bucket.

    Args:
        path_to_file (str): The local path to the file to be uploaded
    """
    logger.info("Authenticating with AWS S3")
    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=Config(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
            read_timeout=7200,
            connect_timeout=7200
        )
    )

    logger.info(f"Uploading file {path_to_file} to S3")

    try:
        client.upload_file(
            path_to_file,
            os.getenv("BUCKET_NAME"),
            path_to_file.split("/")[-1]
        )
    except Exception as e:
        logger.error(f"Failed to upload file {path_to_file} to S3. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to upload file {path_to_file} to S3. Error: {e}")

    try:
        response = client.list_objects_v2(
            Bucket=os.getenv("BUCKET_NAME"),
            Prefix=""
        )
        for content in response.get('Contents', []):
            print(content['Key'])
    except Exception as e:
        logger.error(f"Failed to list the contents of the s3 bucket.")

    logger.info(f"Successfully uploaded file {path_to_file} to S3")

def determine_file_size_s3(file_name):
    """
    Determine the size of a file in an AWS S3 bucket.

    This function authenticates with AWS S3 and retrieves the size of a specified file
    from the configured S3 bucket. The file size is returned in bytes.

    Args:
        file_name (str): The name of the file (excluding the '.csv' extension) whose size is to be determined.

    Returns:
        int: The size of the file in bytes.
    """

    logger.info("Getting object size form AWS S3")
    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=Config(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
        )
    )

    logger.info(f"Accessing file {file_name} from S3")

    object_size = client.head_object(
                Bucket=os.getenv('BUCKET_NAME'),
                Key=file_name + '.csv'
            )["ContentLength"]

    return object_size

def open_file_in_s3(file_name, chunk_size, object_size, chunk_start, chunk_end):
    """
    Retrieve a chunk of data from a file stored in an AWS S3 bucket.

    This function connects to an S3 bucket and retrieves a specific byte range
    from a file as a chunk. If the chunk size is larger than or equal to the
    object size, the entire file is read. Otherwise, a specified range of bytes
    is fetched. This approach helps mitigate timeouts or empty chunks when
    streaming large files.

    Args:
        file_name (str): The name of the file (without the '.csv' extension) to be accessed.
        chunk_size (int): The size of the chunk to be read in bytes.
        object_size (int): The total size of the object in bytes.
        chunk_start (int): The starting byte position for the chunk.
        chunk_end (int): The ending byte position for the chunk.

    Returns:
        tuple: A tuple containing the chunk of data as bytes, and the updated
               chunk_start and chunk_end positions.
    """

    logger.info(f"Getting chunk of {file_name} of size {chunk_size}")

    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=Config(
            request_checksum_calculation="when_required",
            response_checksum_validation="when_required",
            read_timeout=7200,
            connect_timeout=7200
        )
    )
    logger.info(f"Accessing file {file_name} from S3")
    try:
    # Read specific byte range from file as a chunk. We do this because AWS server times out and sends
    # empty chunks when streaming the entire file.
        chunk = None
        if chunk_size >= object_size:
            with smart_open.open(
                f"s3://{os.getenv('BUCKET_NAME')}/{file_name}.csv",
                'rb',
                transport_params={
                    "client":client
                }
            ) as f:
                chunk = f.read()
        else:
            with smart_open.open(
                f"s3://{os.getenv('BUCKET_NAME')}/{file_name}.csv",
                'rb',
                transport_params={
                    "client":client
                }
            ) as f:
                f.seek(chunk_start)
                chunk = f.read(chunk_size)


        chunk_start += chunk_size
        chunk_end += chunk_size

    except Exception as e:
        logger.error(f"Failed to download file {file_name} from S3. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to download file {file_name} from S3. Error: {e}")

    logger.info(f"Successfully Accessed file {file_name} from S3")

    return chunk, chunk_start, chunk_end

def check_temp_dir_exists():
    """
    Checks if the temp directory exists and creates it if it doesn't.
    The temp directory is used to store the csv files before they are uploaded to S3.
    """
    try:
        abs_path = pathlib.Path(__file__).parent.resolve()
        temp_dir = os.path.join(abs_path, "temp")
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create the temp directory. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to create temp directory. Error: {e}")

def clean_aws_s3_bucket():
    """
    Deletes all files from the S3 bucket specified in the environment variable BUCKET_NAME.
    """

    logger.info("Authenticating with AWS S3")

    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=Config(request_checksum_calculation="when_required", response_checksum_validation="when_required")
    )

    try:
        response = client.list_objects_v2(
            Bucket=os.getenv("BUCKET_NAME"),
            Prefix=""
        )
        for content in response.get('Contents', []):
            logger.info(f"Deleting {content["Key"]} From the Bucket!")

            client.delete_object(
                Bucket=os.getenv("BUCKET_NAME"),
                Key=content["Key"]
            )
    except Exception as e:
        logger.error(f"Delete {content["Key"]} From the S3 Bucket!")

def make_table_from_to_db(table, query, schema, dtype):
    """
    Populate a table in the destination database from data that already exists in the destination database.

    Args:
        table (str): The name of the table to populate.
        query (str): The SQL query to get the data from the destination database.
        schema (str): The schema of the table to populate.
        dtype (dict): A dictionary specifying the data types of the columns in the table.

    Returns:
        int: The number of rows inserted into the table.
    """
    logger.info("Making table out of the data that already exists in the destination DB")
    try:
        conn = get_to_conn()
        cur = conn.cursor()

        df = pl.read_database(query=query, connection=conn, schema_overrides=dtype)

        rows = df.rows()
        cols = df.columns

        insert_query = f"INSERT INTO {schema}.{table}({", ".join(cols)}) VALUES %s ON CONFLICT ON CONSTRAINT {table}_pkey DO NOTHING;"

        execute_values(cur=cur, sql=insert_query, argslist=rows)

        conn.commit()
    except Exception as e:
        logger.error(f"Failed to insert into the table {table}. Error: {e}",exc_info=True)
        raise RuntimeError(f"Failed to insert into the table {table}. Error: {e}")
    finally:
        conn.close()
        cur.close()

    return len (df)

def get_contents_of_bucket():

    """
    Get the contents of the S3 bucket specified in the BUCKET_NAME environment variable.

    This function connects to an S3 bucket and retrieves a list of all objects in the bucket.
    It then prints out each object's key.

    Args:
        None

    Returns:
        None
    """
    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=Config(request_checksum_calculation="when_required", response_checksum_validation="when_required")
    )

    try:
        response = client.list_objects_v2(
            Bucket=os.getenv("BUCKET_NAME"),
            Prefix=""
        )
        for content in response.get('Contents', []):
            print(content["Key"])

    except Exception as e:
        logger.error(f"Failed to get list of files From the S3 Bucket!")

def construct_insert_tables( station_metadata):
    """
    This method will construct the dataframes that consists of the metadata required to insert new stations into the database.

    Args:
        station_metadata (polars.DataFrame): Polars DataFrame object with the metadata required for each station. Columns include:
            **FILL COLUMNS**

    Output:
        new_stations (polars.DataFrame): Polars DataFrame object the new sation data for the station table.
        new_station_insert_dict (dict): Dictionary that contains the data required to insert into the following tables:
            - station_project_id
            - station_variable
            - station_year
            - station_type_id
            - station_network_id
    """

    new_station_insert_dict = NEW_STATION_INSERT_DICT_TEMPLATE.copy()

    try:
        # Collect the new station data to be inserted in to station table
        new_stations = (
            station_metadata
            .select(
                "original_id",
                "network_id",
                "type_id",
                "station_name",
                "station_status_id",
                "longitude",
                "latitude",
                "scrape",
                "stream_name",
                "station_description",
                "operation_id",
                "drainage_area",
                "regulated",
                "user_flag"
            )
            .unique()
        ).collect()

        for key in new_station_insert_dict.keys():
            data_df =(
                station_metadata
                .filter(pl.col(new_station_insert_dict[key][0]).is_not_null())
                .select(
                    pl.col("original_id"),
                    pl.col(new_station_insert_dict[key][0]).cast(pl.List(pl.Int32))
                )
                .unique()
                .explode(new_station_insert_dict[key][0])
            ).collect()

            new_station_insert_dict[key].append(data_df)

    except Exception as e:
        logger.error(f"Error when trying to construct the insert dataframes. Will continue without inserting new stations. Error {e}")
        raise RuntimeError(e)

    return new_stations, new_station_insert_dict

def insert_new_stations(new_stations, metadata_dict, db_conn):
    """
    If a new station is found, there are some metadata that needs to be inserted in other tables. This function is the collection of all insertions that should happen when new stations are found that are not yet in the DB. After the insertion, an email will be sent to the data team to notify them of the new data, and request a review of the data.

    Args:
        new_stations (polars.DataFrame): Polars DataFrame object with the the following columns:
        Required
            original_id: string
            station_name: string
            station_status_id: integer
            longitude: float
            latitude: float
            scrape: boolean
        Optional:
            stream_name: string
            station_description: string
            operation_id: integer
            geom4326: geometry
            drainage_area: float
            regulated: boolean
            user_flag: boolean

        station_project (polars.DataFrame): Polars DataFrame object with the the following columns:
        Required
            original_id: string
            project_id: integer

        station_variable (polars.DataFrame): Polars DataFrame object with the the following columns:
        Required
            original_id: string
            variable_id: integer

        station_year (polars.DataFrame): Polars DataFrame object with the the following columns:
        Required
            original_id: string
            year: integer

        station_type_id (polars.DataFrame): Polars DataFrame object with the the following columns:
        Required
            original_id: string
            type_id: integer

    Output:
        None
    """
    try:

        ids = new_stations.get_column("original_id").to_list()
        id_list = ", ".join(f"'{id}'" for id in ids)

        logger.debug("Inserting new stations to station table")
        columns = new_stations.columns
        rows = new_stations.rows()
        query = f"""INSERT INTO bcwat_obs.station({', '.join(columns)}) VALUES %s;"""

        cursor = db_conn.cursor()

        execute_values(cursor, query, rows, page_size=100000)

    except Exception as e:
        db_conn.rollback()
        logger.error(f"Error when inserting new stations, error: {e}")
        raise RuntimeError(f"Error when inserting new stations, error: {e}")

    logger.debug("Getting new updated station_list")

    # Get station_ids of stations that were just inserted
    try:
        query = f"""
            SELECT original_id, station_id
            FROM bcwat_obs.station
            WHERE original_id IN ({id_list});
        """

        new_station_ids = pl.read_database(query, connection=db_conn, schema_overrides={"original_id": pl.String, "station_id": pl.Int64})

    except Exception as e:
        db_conn.rollback()
        logger.error(f"Error when getting id's for the new stations that were inserted")
        raise RuntimeError(e)

    cursor = db_conn.cursor()

    for key in metadata_dict.keys():
        try:
            logger.debug(f"Inserting station information in to {key} table.")
            # Joining the new stations with the station_list to get the new station_id
            metadata_df = metadata_dict[key][1].join(new_station_ids, on="original_id", how="inner").select("station_id", metadata_dict[key][0])
            columns = metadata_df.columns
            rows = metadata_df.rows()

            query = f"""INSERT INTO {key}({', '.join(columns)}) VALUES %s ON CONFLICT (station_id, {metadata_dict[key][0]}) DO NOTHING;"""

            execute_values(cursor, query, rows, page_size=100000)

        except Exception as e:
            db_conn.rollback()
            logger.error(f"Error when inserting new {key} rows, error: {e}")
            raise RuntimeError(f"Error when inserting new {key} rows, error: {e}")

    # Only commit if everything succeeded
    db_conn.commit()

    logger.debug("New stations have been inserted into the database.")
