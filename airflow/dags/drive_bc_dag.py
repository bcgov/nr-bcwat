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
    dag_id="drive_bc_dag",
    schedule_interval="30 * * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "hourly"]
)
def run_drive_bc_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="drive_bc_scraper"
    )
    def run_drive_bc(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.drive_bc import DriveBcPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        drive_bc = DriveBcPipeline(date_now=logical_time, db_conn=conn)

        drive_bc.download_data()
        drive_bc.validate_downloaded_data()
        drive_bc.transform_data()
        drive_bc.load_data()
        drive_bc.check_year_in_station_year()
        logger.info("There is no data for drive_bc at the moment. Exiting.")

    run_drive_bc()

run_drive_bc_scraper = run_drive_bc_scraper()
