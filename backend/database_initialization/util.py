import logging
import os
import psycopg2 as pg2
from psycopg2.extensions import AsIs
from dotenv import load_dotenv, find_dotenv
from constants import logger

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
    return pg2.connect(
        host=fromhost,
        port=fromport,
        user=fromuser,
        password=frompass,
        dbname=fromdb
    )

def get_to_conn():
    return pg2.connect(
        host=tohost,
        port=toport,
        user=touser,
        password=topass,
        dbname=todb
    )

def get_wet_conn():
    return pg2.connect(
        host=wethost,
        port=wetport,
        user=wetuser,
        password=wetpass,
        dbname=wetdb
    )


def recreate_db_schemas():
    from queries.bcwat_watershed_erd_diagram import bcwat_ws_query
    from queries.bcwat_obs_erd_diagram import bcwat_obs_query
    from queries.bcwat_licence_erd_diagram import bcwat_lic_query

    to_conn = get_to_conn()
    cur = to_conn.cursor()

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

def special_variable_function(df):
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
    return df
