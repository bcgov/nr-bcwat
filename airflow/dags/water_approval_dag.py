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
    dag_id="wls_water_approval_dag",
    schedule_interval="0 5 * * *",
    start_date=pendulum.datetime(2025, 5, 29, tz="UTC"),
    catchup=False,
    tags=["licence", "databc", "daily"]
)
def run_water_approval_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="water_approval_scraper"
    )
    def run_water_approval(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.DataBcPipeline.licences.water_approval_points import WaterApprovalPointsPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        water_approval_scraper = WaterApprovalPointsPipeline(date_now=logical_time, db_conn=conn)

        water_approval_scraper.download_data()
        water_approval_scraper.validate_downloaded_data()
        water_approval_scraper.transform_data()
        water_approval_scraper.load_data()

    run_water_approval()

run_water_approval_scraper = run_water_approval_scraper()
