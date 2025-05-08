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

default_args = {
    'email': ['technical@foundryspatial.com'],
    'email_on_failure': True
}

@dag(
    dag_id="gw_moe_dag",
    schedule_interval="30 8 * * *",
    start_date=pendulum.datetime(2025, 4, 17, tz="UTC"),
    catchup=False,
    tags=["groundwater", "station_observations", "daily"],
    default_args=default_args
)
def run_gw_moe_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="gw_moe_scraper"
    )
    def run_gw_moe(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe import GwMoePipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        gw_moe = GwMoePipeline(date_now=logical_time, db_conn=conn)

        gw_moe.download_data()
        gw_moe.validate_downloaded_data()
        gw_moe.transform_data()
        gw_moe.load_data()
        gw_moe.check_year_in_station_year()

    run_gw_moe()

run_gw_moe_scraper = run_gw_moe_scraper()
