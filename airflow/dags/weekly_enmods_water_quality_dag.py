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
    dag_id="weekly_ems_water_quality_dag",
    schedule="30 8 * * 0",
    start_date=datetime(2025, 7, 3),
    catchup=False,
    tags=["waterquality"],
    default_args=generate_default_args(PLATFORM)
)
def run_weekly_enmods_water_quality_dag():

    @task(
        executor_config=generate_executor_config_template('largest'),
        task_id="weekly_ems_water_quality"
    )
    def run_weekly_enmods_water_quality(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.enmods_archive_update import QuarterlyEnmodsArchiveUpdatePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        ems_weekly_scraper = QuarterlyEnmodsArchiveUpdatePipeline(date_now=logical_time, db_conn=conn, quarterly=False)

        ems_weekly_scraper.download_data()
        ems_weekly_scraper.transform_data()
        ems_weekly_scraper.clean_up()

    run_weekly_enmods_water_quality()

run_weekly_ems_water_quality = run_weekly_enmods_water_quality_dag()
