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
    dag_id="quarterly_ems_water_quality_dag",
    # Cron for At 08:30 UTC (00:30 PST) on day-of-month 2 in every 3rd month.
    schedule="30 8 2 */3 *",
    start_date=datetime(2025, 7, 3),
    catchup=False,
    tags=["waterquality", "quarterly"],
    default_args=generate_default_args(PLATFORM)
)
def run_quarterly_ems_water_quality_dag():

    @task(
        executor_config=generate_executor_config_template('largest'),
        task_id="quarterly_ems_water_quality"
    )
    def run_quarterly_ems_water_quality(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.ems_archive_update import QuarterlyEmsArchiveUpdatePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        ems_quarterly_scraper = QuarterlyEmsArchiveUpdatePipeline(date_now=logical_time, db_conn=conn)

        ems_quarterly_scraper.download_data()
        ems_quarterly_scraper.download_historical_data()
        ems_quarterly_scraper.download_station_data_from_databc()
        ems_quarterly_scraper.transform_data()
        ems_quarterly_scraper.clean_up()

    run_quarterly_ems_water_quality()


run_quarterly_ems_water_quality = run_quarterly_ems_water_quality_dag()
