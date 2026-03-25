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
    dag_id="env_aqn_dag",
    schedule="0 8 * * *",
    start_date=datetime(2025, 5, 15),
    catchup=False,
    tags=["climate", "station_observations", "daily"],
    default_args=generate_default_args(ENVIRONMENT)
)
def run_env_aqn_scraper():

    @task(
        executor_config=generate_executor_config_template('small', ENVIRONMENT),
        task_id="env_aqn_scraper"
    )
    def run_env_aqn(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.env_aqn import EnvAqnPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        env_aqn = EnvAqnPipeline(date_now=logical_time, db_conn=conn)

        env_aqn.download_data()
        env_aqn.validate_downloaded_data()
        env_aqn.transform_data()
        env_aqn.load_data()
        env_aqn.check_year_in_station_year()

    run_env_aqn()

run_env_aqn_scraper = run_env_aqn_scraper()
