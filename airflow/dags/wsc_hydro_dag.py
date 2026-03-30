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
    dag_id="wsc_hydro_dag",
    schedule="0 8 * * *",
    start_date=datetime(2025, 4, 17),
    catchup=False,
    tags=["water", "station_observations", "daily"],
    default_args=generate_default_args(PLATFORM)
)
def run_wsc_hydro_scraper():

    @task(
        executor_config=generate_executor_config_template('medium'),
        task_id="wsc_hydro_scraper"
    )
    def run_wsc_hydro(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline

        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        wsc_hydro = WscHydrometricPipeline(date_now=logical_time, db_conn=conn)

        wsc_hydro.download_data()
        wsc_hydro.validate_downloaded_data()
        wsc_hydro.transform_data()
        wsc_hydro.load_data()
        wsc_hydro.check_year_in_station_year()

    run_wsc_hydro()

run_wsc_hydro_scraper = run_wsc_hydro_scraper()
