import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/medium_task_template.yaml"
    }

default_args = {
    'email': ['technical@foundryspatial.com'],
    'email_on_failure': True
}

@dag(
    dag_id="asp_dag",
    schedule_interval="0 3 * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["water","climate", "station_observations", "daily"],
    default_args=default_args
)
def run_asp_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="asp_scraper"
    )
    def run_asp(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.asp import AspPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        asp = AspPipeline(date_now=logical_time, db_conn=conn)

        asp.download_data()
        asp.validate_downloaded_data()
        asp.transform_data()
        asp.check_number_of_stations_scraped()
        asp.load_data()
        asp.check_year_in_station_year()

    run_asp()

run_asp_scraper = run_asp_scraper()
