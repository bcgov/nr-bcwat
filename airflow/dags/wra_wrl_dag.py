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
    dag_id="wra_wrl_dag",
    schedule_interval="45 5 * * *",
    start_date=pendulum.datetime(2025, 6, 5, tz="UTC"),
    catchup=False,
    tags=["licence","databc", "daily"],
    default_args=default_args
)
def run_wra_wrl_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="wra_scraper"
    )
    def run_wra(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_applications_public import WaterRightsApplicationsPublicPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        wra_scraper = WaterRightsApplicationsPublicPipeline(date_now=logical_time, db_conn=conn)

        wra_scraper.download_data()
        wra_scraper.validate_downloaded_data()
        wra_scraper.transform_data()
        wra_scraper.load_data()

    @task(
        executor_config=executor_config_template,
        task_id="wrl_scraper"
    )
    def run_wrl(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_licences_public import WaterRightsLicencesPublicPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        wrl_scraper = WaterRightsLicencesPublicPipeline(date_now=logical_time, db_conn=conn)

        wrl_scraper.download_data()
        wrl_scraper.validate_downloaded_data()
        wrl_scraper.transform_data()
        wrl_scraper.load_data()

    @task(
        executor_config=executor_config_template,
        task_id="combined_and_load",
        trigger_rule="all_success"
    )
    def run_combine(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.DataBcPipeline.licences.water_rights_applications_public import WaterRightsApplicationsPublicPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        wra_scraper = WaterRightsApplicationsPublicPipeline(date_now=logical_time, db_conn=conn)

        wra_scraper.transform_bc_wls_wrl_wra_data()
        wra_scraper.load_data()

    [run_wrl(), run_wra()] >> run_combine()

run_asp_scraper = run_wra_wrl_scraper()
