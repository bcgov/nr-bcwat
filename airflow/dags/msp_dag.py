import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/medium_task_template.yaml"
    }

@dag(
    dag_id="msp_dag",
    schedule_interval="45 4 * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["water","climate", "station_observations", "daily"]
)
def run_msp_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="msp_scraper"
    )
    def run_msp(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.msp import MspPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        msp = MspPipeline(date_now=logical_time, db_conn=conn)

        msp.download_data()
        msp.validate_downloaded_data()
        msp.transform_data()
        if not msp._EtlPipeline__transformed_data["msp"]["df"].is_empty():
            msp.check_number_of_stations_scraped()
            msp.load_data()
            msp.check_year_in_station_year()
        else:
            logger.info("There is no data for MSP at the moment. Exiting.")

    run_msp()

run_msp_scraper = run_msp_scraper()
