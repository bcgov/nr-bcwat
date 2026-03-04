import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="bc_ogc_dag",
    schedule="0 6 * * *",
    start_date=datetime(2025, 5, 29),
    catchup=False,
    tags=["licence", "databc", "daily"],
    default_args=default_args
)
def run_short_term_approval_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
        task_id="short_term_approval_scraper"
    )
    def run_short_term_approval(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.DataBcPipeline.licences.water_licences_bcer import WaterLicencesBCERPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        short_term_approval_scraper = WaterLicencesBCERPipeline(date_now=logical_time, db_conn=conn)

        short_term_approval_scraper.download_data()
        short_term_approval_scraper.validate_downloaded_data()
        short_term_approval_scraper.transform_data()
        short_term_approval_scraper.load_data()

    run_short_term_approval()

run_short_term_approval_scraper = run_short_term_approval_scraper()
