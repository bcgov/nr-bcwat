import os
import pendulum
from airflow.decorators import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="flowworks_dag",
    schedule_interval="0 8 * * *",
    start_date=pendulum.datetime(2025, 4, 17, tz="UTC"),
    catchup=False,
    tags=["water","climate", "station_observations", "daily"],
    default_args=default_args
)
def run_flowworks_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
        task_id="flowworks_scraper"
    )
    def run_flowworks(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.flow_works import FlowWorksPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        flowworks = FlowWorksPipeline(date_now=logical_time, db_conn=conn)

        flowworks.download_data()
        flowworks.validate_downloaded_data()
        flowworks.transform_data()
        flowworks.load_data()
        flowworks.check_year_in_station_year()

    run_flowworks()

run_flowworks_scraper = run_flowworks_scraper()
