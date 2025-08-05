import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/heavy_task_template.yaml"
    }

@dag(
    dag_id="quarterly_moe_hydrometric_historic_update_dag",
    # Cron for At 05:00 on day-of-month 1 in every 3rd month.
    schedule_interval="0 5 1 */3 *",
    start_date=pendulum.datetime(2025, 6, 13, tz="UTC"),
    catchup=False,
    tags=["water", "quarterly"]
)
def run_quarterly_moe_hydrometric_historic_update_dag():

    @task(
        executor_config=executor_config_template,
        task_id="quarterly_moe_hydrometric_hitoric_update_discharge"
    )
    def run_quarterly_moe_hydrometric_historic_update(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic import QuarterlyMoeHydroHistoricPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        moe_hydro_hist_scraper = QuarterlyMoeHydroHistoricPipeline(date_now=logical_time, db_conn=conn, archive_type="Discharge")

        moe_hydro_hist_scraper.download_data()
        moe_hydro_hist_scraper.validate_downloaded_data()
        moe_hydro_hist_scraper.get_and_insert_new_stations()
        moe_hydro_hist_scraper.transform_data()
        moe_hydro_hist_scraper.load_data()

    @task(
        executor_config=executor_config_template,
        task_id="daily_moe_hydrometric_historic_update_stage"
    )
    def run_daily_moe_hydrometric_historic(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.moe_hydrometric_historic import QuarterlyMoeHydroHistoricPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        moe_hydro_hist_scraper = QuarterlyMoeHydroHistoricPipeline(date_now=logical_time, db_conn=conn, archive_type="Stage")

        moe_hydro_hist_scraper.download_data()
        moe_hydro_hist_scraper.validate_downloaded_data()
        moe_hydro_hist_scraper.get_and_insert_new_stations()
        moe_hydro_hist_scraper.transform_data()
        moe_hydro_hist_scraper.load_data()

    run_quarterly_moe_hydrometric_historic_update() >> run_daily_moe_hydrometric_historic()


run_quarterly_moe_hydrometric_historic_update = run_quarterly_moe_hydrometric_historic_update_dag()
