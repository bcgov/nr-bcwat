import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

environment = os.getenv("AIRFLOW_ENVIRONMENT")

if environment == "okd":
    executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/okd/medium_task_template.yaml"
    }
elif environment =="openshift":
    executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/openshift/medium_task_template.yaml"
    }

@dag(
    dag_id="env_aqn_dag",
    schedule_interval="30 3 * * *",
    start_date=pendulum.datetime(2025, 5, 15, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "daily"]
)
def run_env_aqn_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="env_aqn_scraper"
    )
    def run_env_aqn(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.env_aqn import EnvAqnPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        env_aqn = EnvAqnPipeline(date_now=logical_time, db_conn=conn)

        env_aqn.download_data()
        env_aqn.validate_downloaded_data()
        env_aqn.transform_data()
        env_aqn.check_number_of_stations_scraped()
        env_aqn.load_data()
        env_aqn.check_year_in_station_year()

    run_env_aqn()

run_env_aqn_scraper = run_env_aqn_scraper()
