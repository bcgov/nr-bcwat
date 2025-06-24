import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
    "pod_template_file": "/opt/airflow/pod_templates/heavy_task_template.yaml",
    "pod_override": k8s.V1Pod(
        metadata=k8s.V1ObjectMeta(labels={"release": "stable"})
    ),
}

@dag(
    dag_id="quarterly_hydat_dag",
    # Cron for At 02:00 on day-of-month 1 in every 3rd month.
    schedule_interval="0 2 1 */3 *",
    start_date=pendulum.datetime(2025, 6, 13, tz="UTC"),
    catchup=False,
    tags=["water", "quarterly", "hydat"]
)
def run_quarterly_hydat_import_dag():

    @task(
        executor_config=executor_config_template,
        task_id="quarterly_hydat_import"
    )
    def run_quarterly_hydat_import(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.QuarterlyPipeline.quarterly.hydat_import import HydatPipeline
        from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        hydat_scraper = HydatPipeline(date_now=logical_time, db_conn=conn)

        if hydat_scraper.will_import:
            logger.info(f"New Verison of Hydat is available. Downloading and importing data")
            hydat_scraper.download_data()
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

    run_quarterly_hydat_import()

run_quarterly_hydat_import = run_quarterly_hydat_import_dag()
