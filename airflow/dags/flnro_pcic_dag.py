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
    dag_id="flnro_pcic_dag",
    schedule_interval="30 21 * * *",
    start_date=pendulum.datetime(2025, 5, 15, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "daily"]
)
def run_flnro_pcic_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="flnro_pcic_scraper"
    )
    def run_flnro_pcic(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.flnro_pcic import FlnroWmbPcicPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        flnro_pcic = FlnroWmbPcicPipeline(date_now=logical_time, db_conn=conn)

        flnro_pcic.download_data()
        flnro_pcic.validate_downloaded_data()
        flnro_pcic.transform_data()
        flnro_pcic.check_number_of_stations_scraped()
        flnro_pcic.load_data()
        flnro_pcic.check_year_in_station_year()

    run_flnro_pcic()

run_flnro_pcic_scraper = run_flnro_pcic_scraper()
