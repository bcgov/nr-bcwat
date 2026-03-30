import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.functions import (
    generate_default_args,
    generate_executor_config_template
)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

PLATFORM = os.getenv('PLATFORM', 'no-platform-found')

@dag(
    dag_id="quarterly_ec_update_dag",
    # Cron for At 08:30 UTC (00:30 PST) on day-of-month 1 in every 3rd month.
    schedule="30 8 1 */3 *",
    start_date=datetime(2025, 6, 13),
    catchup=False,
    tags=["climate", "quarterly"],
    default_args=generate_default_args(PLATFORM)
)
def run_quarterly_ec_update_dag():

    @task(
        executor_config=generate_executor_config_template('medium'),
        task_id="quarterly_ec_update"
    )
    def run_quarterly_ec_update(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.climate_ec_update import QuarterlyEcUpdatePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        quarterly_ec_update = QuarterlyEcUpdatePipeline(date_now=logical_time, db_conn=conn)

        quarterly_ec_update.download_data()
        quarterly_ec_update.validate_downloaded_data()
        quarterly_ec_update.transform_data()
        quarterly_ec_update.load_data()

    run_quarterly_ec_update()

run_quarterly_ec_update = run_quarterly_ec_update_dag()
