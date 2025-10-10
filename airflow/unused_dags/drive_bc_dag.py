import os
import pendulum
from airflow.decorators import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="drive_bc_dag",
    schedule_interval="30 * * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "hourly"],
    default_args=default_args
)
def run_drive_bc_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
        task_id="drive_bc_scraper"
    )
    def run_drive_bc(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.drive_bc import DriveBcPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        drive_bc = DriveBcPipeline(date_now=logical_time, db_conn=conn)

        drive_bc.download_data()
        drive_bc.validate_downloaded_data()
        drive_bc.transform_data()
        drive_bc.load_data()
        drive_bc.check_year_in_station_year()
        logger.info("There is no data for drive_bc at the moment. Exiting.")

    run_drive_bc()

run_drive_bc_scraper = run_drive_bc_scraper()
