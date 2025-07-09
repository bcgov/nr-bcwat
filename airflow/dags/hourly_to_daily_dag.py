import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/medium_task_template.yaml"
    }

@dag(
    dag_id="convert_hourly_to_daily_dag",
    schedule_interval="0 13 * * *",
    start_date=pendulum.datetime(2025, 5, 9, tz="UTC"),
    catchup=False,
    tags=["climate", "conversions", "daily"]
)
def run_hourly_to_daily_converter():

    @task(
        executor_config=executor_config_template,
        task_id="drive_bc_scraper"
    )
    def run_converter(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.drive_bc import DriveBcPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        drive_bc_hourly_to_daily_converter = DriveBcPipeline(date_now=logical_time, db_conn=conn)

        drive_bc_hourly_to_daily_converter.convert_hourly_data_to_daily_data()
        drive_bc_hourly_to_daily_converter.load_data()

    run_converter()

run_drive_bc_scraper = run_hourly_to_daily_converter()
