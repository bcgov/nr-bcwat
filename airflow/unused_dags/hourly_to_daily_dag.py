import os
import pendulum
from airflow.decorators import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template

@dag(
    dag_id="convert_hourly_to_daily_dag",
    schedule_interval="0 13 * * *",
    start_date=pendulum.datetime(2025, 5, 9, tz="UTC"),
    catchup=False,
    tags=["climate", "conversions", "daily"]
)
def run_hourly_to_daily_converter():

    @task(
        executor_config=generate_executor_config_template('tiny'),
        task_id="drive_bc_scraper"
    )
    def run_converter(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.drive_bc import DriveBcPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        drive_bc_hourly_to_daily_converter = DriveBcPipeline(date_now=logical_time, db_conn=conn)

        drive_bc_hourly_to_daily_converter.convert_hourly_data_to_daily_data()
        drive_bc_hourly_to_daily_converter.load_data()

    run_converter()

run_drive_bc_scraper = run_hourly_to_daily_converter()
