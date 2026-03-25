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
    dag_id="quarterly_moe_gw_update",
    # Cron for At 09:00 UTC (01:00 PST) on day-of-month 1 in every 3rd month.
    schedule="0 9 1 */3 *",
    start_date=datetime(2025, 6, 13),
    catchup=False,
    tags=["groundwater", "quarterly"],
    default_args=generate_default_args(ENVIRONMENT)
)
def run_quarterly_gw_moe_update_dag():

    @task(
        executor_config=generate_executor_config_template('medium', ENVIRONMENT),
        task_id="quarterly_gw_moe_update"
    )
    def run_quarterly_gw_moe_update(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe import GwMoePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        gw_quarterly_scraper = GwMoePipeline(date_now=logical_time, db_conn=conn, quarterly=True)

        gw_quarterly_scraper.download_data()
        gw_quarterly_scraper.validate_downloaded_data()
        gw_quarterly_scraper.transform_data()
        gw_quarterly_scraper.load_data()

    @task(
        executor_config=generate_executor_config_template('medium', ENVIRONMENT),
        task_id="daily_gw_moe_update"
    )
    def run_daily_gw_moe(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe import GwMoePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        gw_daily_scraper = GwMoePipeline(date_now=logical_time, db_conn=conn, quarterly=False)

        gw_daily_scraper.download_data()
        gw_daily_scraper.validate_downloaded_data()
        gw_daily_scraper.transform_data()
        gw_daily_scraper.load_data()
        gw_daily_scraper.check_year_in_station_year()

    run_quarterly_gw_moe_update() >> run_daily_gw_moe()


run_quarterly_gw_moe_update = run_quarterly_gw_moe_update_dag()
