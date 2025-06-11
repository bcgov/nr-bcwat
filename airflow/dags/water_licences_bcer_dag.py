import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
    "pod_template_file": "/opt/airflow/pod_templates/medium_task_template.yaml",
    "pod_override": k8s.V1Pod(
        metadata=k8s.V1ObjectMeta(labels={"release": "stable"})
    ),
}

@dag(
    dag_id="bc_ogc_dag",
    schedule_interval="0 6 * * *",
    start_date=pendulum.datetime(2025, 5, 29, tz="UTC"),
    catchup=False,
    tags=["licence", "databc", "daily"]
)
def run_short_term_approval_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="short_term_approval_scraper"
    )
    def run_short_term_approval(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer import WaterLicencesBCERPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        short_term_approval_scraper = WaterLicencesBCERPipeline(date_now=logical_time, db_conn=conn)

        short_term_approval_scraper.download_data()
        short_term_approval_scraper.validate_downloaded_data()
        short_term_approval_scraper.transform_data()
        short_term_approval_scraper.load_data()

    run_short_term_approval()

run_short_term_approval_scraper = run_short_term_approval_scraper()
