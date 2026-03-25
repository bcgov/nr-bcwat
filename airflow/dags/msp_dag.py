import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.functions import (
    generate_default_args,
    generate_executor_config_template
)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

PLATFORM = os.getenv('PLATFORM', 'no-platform-found')

@dag(
    dag_id="msp_dag",
    schedule="0 8 * * *",
    start_date=datetime(2025, 5, 7),
    catchup=False,
    tags=["water","climate", "station_observations", "daily"],
    default_args=generate_default_args(PLATFORM)
)
def run_msp_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny'),
        task_id="msp_scraper"
    )
    def run_msp(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.msp import MspPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        msp = MspPipeline(date_now=logical_time, db_conn=conn)

        msp.download_data()
        msp.validate_downloaded_data()
        msp.transform_data()
        if not msp._EtlPipeline__transformed_data["msp"]["df"].is_empty():
            msp.load_data()
            msp.check_year_in_station_year()
        else:
            logger.info("There is no data for MSP at the moment. Exiting.")

    run_msp()

run_msp_scraper = run_msp_scraper()
