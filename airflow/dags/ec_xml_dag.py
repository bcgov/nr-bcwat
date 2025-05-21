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
    dag_id="ec_xml_dag",
    schedule_interval="0 11 * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "daily"]
)
def run_ec_xml_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="ec_xml_scraper"
    )
    def run_ec_xml(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml import EcXmlPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        ec_xml = EcXmlPipeline(date_now=logical_time, db_conn=conn)

        ec_xml.download_data()
        ec_xml.validate_downloaded_data()
        ec_xml.transform_data()
        ec_xml.check_number_of_stations_scraped()
        ec_xml.load_data()
        ec_xml.check_year_in_station_year()

    run_ec_xml()

run_ec_xml_scraper = run_ec_xml_scraper()
