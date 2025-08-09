import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/medium_task_template.yaml"
    }

@dag(
    dag_id="quarterly_water_quality_eccc_dag",
    # Cron for At 04:00 on day-of-month 1 in every 3rd month.
    schedule_interval="0 4 1 */3 *",
    start_date=pendulum.datetime(2025, 6, 13, tz="UTC"),
    catchup=False,
    tags=["waterquality", "quarterly"]
)
def run_quarterly_water_quality_eccc_dag():

    @task(
        executor_config=executor_config_template,
        task_id="quarterly_water_quality_eccc"
    )
    def run_quarterly_water_quality_eccc(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.water_quality_eccc import QuarterlyWaterQualityEcccPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        eccc_quarterly_scraper = QuarterlyWaterQualityEcccPipeline(date_now=logical_time, db_conn=conn)

        eccc_quarterly_scraper.download_data()
        eccc_quarterly_scraper.validate_downloaded_data()
        eccc_quarterly_scraper.transform_data()
        eccc_quarterly_scraper.load_data()
        eccc_quarterly_scraper.check_year_in_station_year()

    run_quarterly_water_quality_eccc()


run_quarterly_water_quality_eccc = run_quarterly_water_quality_eccc_dag()
