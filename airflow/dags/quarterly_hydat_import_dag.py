import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="quarterly_hydat_dag",
    # Cron for At 01:30 on day-of-month 1 and 15 of each month.
    # This was done instead of checking every quarter because there is not consistent schedule for Hydat. If there is not a new version of
    # Hydat available. It will not scrape it.
    schedule="30 9 1,15 * *",
    start_date=datetime(2025, 6, 13),
    catchup=False,
    tags=["water", "quarterly", "hydat"],
    default_args=default_args
)
def run_quarterly_hydat_import_dag():

    @task(
        executor_config=generate_executor_config_template('heavy', ENVIRONMENT),
        task_id="quarterly_hydat_import"
    )
    def run_quarterly_hydat_import(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import import HydatPipeline
        from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        hydat_scraper = HydatPipeline(date_now=logical_time, db_conn=conn)

        if hydat_scraper.will_import:
            logger.info(f"New Verison of Hydat is available. Downloading and importing data")
            hydat_scraper.download_data()
            hydat_scraper.extract_data()
            hydat_scraper.get_and_insert_new_stations()

            logger.info("Running WSC Hydrometric Scraper for 365 days")
            wsc_scraper = WscHydrometricPipeline(date_now=logical_time, db_conn=conn, days=365)
            wsc_scraper.download_data()
            wsc_scraper.validate_downloaded_data()
            wsc_scraper.transform_data()
            wsc_scraper.load_data()
            wsc_scraper.check_year_in_station_year()

            hydat_scraper.transform_data()
            hydat_scraper.update_hydat_import_date()
            hydat_scraper.clean_up()

    run_quarterly_hydat_import()

run_quarterly_hydat_import = run_quarterly_hydat_import_dag()
