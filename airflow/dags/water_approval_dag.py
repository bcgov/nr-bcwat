import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="wls_water_approval_dag",
    schedule="0 6 * * *",
    start_date=datetime(2025, 5, 29),
    catchup=False,
    tags=["licence", "databc", "daily"],
    default_args=default_args
)
def run_water_approval_scraper():

    @task(
        executor_config=generate_executor_config_template('medium', ENVIRONMENT),
        task_id="water_approval_scraper"
    )
    def run_water_approval(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.DataBcPipeline.licences.water_approval_points import WaterApprovalPointsPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        water_approval_scraper = WaterApprovalPointsPipeline(date_now=logical_time, db_conn=conn)

        water_approval_scraper.download_data()
        water_approval_scraper.validate_downloaded_data()
        water_approval_scraper.transform_data()
        water_approval_scraper.load_data()

    run_water_approval()

run_water_approval_scraper = run_water_approval_scraper()
