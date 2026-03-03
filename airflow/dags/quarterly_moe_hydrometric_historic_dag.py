import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="quarterly_moe_hydrometric_historic_update_dag",
    # Cron for At 10:00 UTC (02:00 PST) on day-of-month 1 in every 3rd month.
    schedule="0 10 1 */3 *",
    start_date=datetime(2025, 6, 13),
    catchup=False,
    tags=["water", "quarterly"],
    default_args=default_args
)
def run_quarterly_moe_hydrometric_historic_update_dag():

    @task(
        executor_config=generate_executor_config_template('heavy', ENVIRONMENT),
        task_id="quarterly_moe_hydrometric_hitoric_update_discharge"
    )
    def run_quarterly_moe_hydrometric_historic_update(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic import QuarterlyMoeHydroHistoricPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        moe_hydro_hist_scraper = QuarterlyMoeHydroHistoricPipeline(date_now=logical_time, db_conn=conn, archive_type="Discharge")

        moe_hydro_hist_scraper.download_data()
        moe_hydro_hist_scraper.validate_downloaded_data()
        moe_hydro_hist_scraper.get_and_insert_new_stations()
        moe_hydro_hist_scraper.transform_data()
        moe_hydro_hist_scraper.load_data()

    @task(
        executor_config=generate_executor_config_template('heavy', ENVIRONMENT),
        task_id="daily_moe_hydrometric_historic_update_stage"
    )
    def run_daily_moe_hydrometric_historic(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic import QuarterlyMoeHydroHistoricPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        moe_hydro_hist_scraper = QuarterlyMoeHydroHistoricPipeline(date_now=logical_time, db_conn=conn, archive_type="Stage")

        moe_hydro_hist_scraper.download_data()
        moe_hydro_hist_scraper.validate_downloaded_data()
        moe_hydro_hist_scraper.get_and_insert_new_stations()
        moe_hydro_hist_scraper.transform_data()
        moe_hydro_hist_scraper.load_data()

    run_quarterly_moe_hydrometric_historic_update() >> run_daily_moe_hydrometric_historic()


run_quarterly_moe_hydrometric_historic_update = run_quarterly_moe_hydrometric_historic_update_dag()
