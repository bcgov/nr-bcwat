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
    dag_id="flnro_wmb_dag",
    schedule="0 8 * * *",
    start_date=datetime(2025, 5, 15),
    catchup=False,
    tags=["climate", "station_observations", "daily"],
    default_args=generate_default_args(PLATFORM)
)
def run_flnro_wmb_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny'),
        task_id="flnro_wmb_scraper"
    )
    def run_flnro_wmb(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.flnro_wmb import FlnroWmbPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        flnro_wmb = FlnroWmbPipeline(date_now=logical_time, db_conn=conn)

        flnro_wmb.download_data()
        flnro_wmb.validate_downloaded_data()
        flnro_wmb.transform_data()
        flnro_wmb.load_data()
        flnro_wmb.check_year_in_station_year()

    run_flnro_wmb()

run_flnro_wmb_scraper = run_flnro_wmb_scraper()
