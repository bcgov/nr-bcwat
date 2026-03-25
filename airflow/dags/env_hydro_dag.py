import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.functions import (
    generate_default_args,
    generate_executor_config_template
)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="env_hydro_dag",
    schedule="10 8 * * *",
    start_date=datetime(2025, 4, 17),
    catchup=False,
    tags=["water", "station_observations", "daily"],
    default_args=generate_default_args(ENVIRONMENT)
)
def run_env_hydro_scraper():

    @task(
        executor_config=generate_executor_config_template('medium', ENVIRONMENT),
        task_id="env_hydro_scraper"
    )
    def run_env_hydro(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro import EnvHydroPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        env_hydro = EnvHydroPipeline(date_now=logical_time, db_conn=conn)

        env_hydro.download_data()
        env_hydro.validate_downloaded_data()
        env_hydro.transform_data()
        env_hydro.load_data()
        env_hydro.check_year_in_station_year()

    run_env_hydro()

run_env_hydro_scraper = run_env_hydro_scraper()
