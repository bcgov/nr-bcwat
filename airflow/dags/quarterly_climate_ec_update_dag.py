import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/medium_task_template.yaml"
    }

@dag(
    dag_id="quarterly_ec_update_dag",
    # Cron for At 02:00 on day-of-month 1 in every 3rd month.
    schedule_interval="0 2 1 */3 *",
    start_date=pendulum.datetime(2025, 6, 13, tz="UTC"),
    catchup=False,
    tags=["climate", "quarterly"]
)
def run_quarterly_ec_update_dag():

    @task(
        executor_config=executor_config_template,
        task_id="quarterly_ec_update"
    )
    def run_quarterly_ec_update(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.climate_ec_update import QuarterlyEcUpdatePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        quarterly_ec_update = QuarterlyEcUpdatePipeline(date_now=logical_time, db_conn=conn)

        quarterly_ec_update.download_data()
        quarterly_ec_update.validate_downloaded_data()
        quarterly_ec_update.transform_data()
        quarterly_ec_update.load_data()

    run_quarterly_ec_update()

run_quarterly_ec_update = run_quarterly_ec_update_dag()
