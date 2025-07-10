from dotenv import load_dotenv, find_dotenv
from constants import logger
import logging
import os
import boto3
from botocore.client import Config
import psycopg2 as pg2
import polars as pl
import gzip
import shutil
import pathlib
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
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(pathname)s - %(funcName)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def get_from_conn():
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
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5
    )

def get_to_conn():
    return pg2.connect(
        host=tohost,
        port=toport,
        user=touser,
        password=topass,
        dbname=todb,
        sslmode='require',
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5
    )

def get_wet_conn():
    return pg2.connect(
        host=wethost,
        port=wetport,
        user=wetuser,
        password=wetpass,
        dbname=wetdb,
        sslmode='require',
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5
    )


def recreate_db_schemas():
    from queries.bcwat_watershed_erd_diagram import bcwat_ws_query
    from queries.bcwat_obs_erd_diagram import bcwat_obs_query
    from queries.bcwat_licence_erd_diagram import bcwat_lic_query

    to_conn = get_to_conn()
    cur = to_conn.cursor()

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
    logger.info("Authenticating with AWS S3")
    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=Config(request_checksum_calculation="when_required", response_checksum_validation="when_required")
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

def download_file_from_s3(file_name, dest_dir):
    logger.info("Authenticating with AWS S3")

    client = boto3.client(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        config=Config(request_checksum_calculation="when_required", response_checksum_validation="when_required")
    )

    logger.info(f"Downloading file {file_name} from S3")

    try:
        client.download_file(
            os.getenv("BUCKET_NAME"),
            file_name + ".csv.gz",
            os.path.join(dest_dir, file_name + ".csv.gz")
        )
    except Exception as e:
        logger.error(f"Failed to download file {file_name} from S3. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to download file {file_name} from S3. Error: {e}")

    logger.info(f"Successfully downloaded file {file_name} from S3")

    logger.info(f"Decompressing file {file_name}")

    try:
        with gzip.GzipFile(f"{dest_dir}/{file_name}.csv.gz", "rb") as f:
            with open(f"{dest_dir}/{file_name}.csv", "wb") as out:
                shutil.copyfileobj(f, out)

        os.remove(f"{dest_dir}/{file_name}.csv.gz")
    except Exception as e:
        logger.error(f"Failed to decompress the file {file_name}.csv.gz. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to decompress the file {file_name}.csv.gz. Error: {e}")

    logger.info(f"Successfully decompressed {file_name} to destination {dest_dir}/{file_name}.csv")

def check_temp_dir_exists():
    try:
        abs_path = pathlib.Path(__file__).parent.resolve()
        temp_dir = os.path.join(abs_path, "temp")
        pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create the temp directory. Error: {e}", exc_info=True)
        raise RuntimeError(f"Failed to create temp directory. Error: {e}")
