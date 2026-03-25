import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.functions import (
    generate_default_args,
    generate_executor_config_template
)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="quarterly_water_quality_eccc_dag",
    # Cron for At 10:15 UTC (02:15 PST) on day-of-month 1 in every 3rd month.
    schedule="15 10 1 */3 *",
    start_date=datetime(2025, 6, 13),
    catchup=False,
    tags=["waterquality", "quarterly"],
    default_args=generate_default_args(ENVIRONMENT)
)
def run_quarterly_water_quality_eccc_dag():

    @task(
        executor_config=generate_executor_config_template('medium', ENVIRONMENT),
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
