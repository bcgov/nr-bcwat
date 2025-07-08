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
    dag_id="quarterly_ems_water_quality_dag",
    # Cron for At 05:00 on day-of-month 1 in every 3rd month.
    schedule_interval="0 5 1 */3 *",
    start_date=pendulum.datetime(2025, 7, 3, tz="UTC"),
    catchup=False,
    tags=["waterquality", "quarterly"]
)
def run_quarterly_ems_water_quality_dag():

    @task(
        executor_config=executor_config_template,
        task_id="quarterly_ems_water_quality"
    )
    def run_quarterly_ems_water_quality(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update import QuarterlyEmsArchiveUpdatePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        ems_quarterly_scraper = QuarterlyEmsArchiveUpdatePipeline(date_now=logical_time, db_conn=conn)

        ems_quarterly_scraper.download_data()
        ems_quarterly_scraper.download_historical_data()
        ems_quarterly_scraper.download_station_data_from_databc()
        ems_quarterly_scraper.transform_data()

    run_quarterly_ems_water_quality()


run_quarterly_ems_water_quality = run_quarterly_ems_water_quality_dag()
