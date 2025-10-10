import os
import pendulum
from airflow.decorators import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="asp_dag",
    schedule_interval="5 8 * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["water","climate", "station_observations", "daily"],
    default_args=default_args
)
def run_asp_scraper():

    @task(
        executor_config=generate_executor_config_template('medium', ENVIRONMENT),
        task_id="asp_scraper"
    )
    def run_asp(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.asp import AspPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        asp = AspPipeline(date_now=logical_time, db_conn=conn)

        asp.download_data()
        asp.validate_downloaded_data()
        asp.transform_data()
        asp.load_data()
        asp.check_year_in_station_year()

    run_asp()

run_asp_scraper = run_asp_scraper()
