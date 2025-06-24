import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
    "pod_template_file": "/opt/airflow/pod_templates/medium_task_template.yaml",
    "pod_override": k8s.V1Pod(
        metadata=k8s.V1ObjectMeta(labels={"release": "stable"})
    ),
}

@dag(
    dag_id="quarterly_moe_gw_update",
    # Cron for At 03:00 on day-of-month 1 in every 3rd month.
    schedule_interval="0 3 1 */3 *",
    start_date=pendulum.datetime(2025, 6, 13, tz="UTC"),
    catchup=False,
    tags=["groundwater", "quarterly"]
)
def run_quarterly_gw_moe_update_dag():

    @task(
        executor_config=executor_config_template,
        task_id="quarterly_gw_moe_update"
    )
    def run_quarterly_gw_moe_update(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe import GwMoePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        gw_quarterly_scraper = GwMoePipeline(date_now=logical_time, db_conn=conn, quarterly=True)

        gw_quarterly_scraper.download_data()
        gw_quarterly_scraper.validate_downloaded_data()
        gw_quarterly_scraper.transform_data()
        gw_quarterly_scraper.load_data()

    @task(
        executor_config=executor_config_template,
        task_id="daily_gw_moe_update"
    )
    def run_daily_gw_moe(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.gw_moe import GwMoePipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        gw_daily_scraper = GwMoePipeline(date_now=logical_time, db_conn=conn, quarterly=False)

        gw_daily_scraper.download_data()
        gw_daily_scraper.validate_downloaded_data()
        gw_daily_scraper.transform_data()
        gw_daily_scraper.load_data()
        gw_daily_scraper.check_year_in_station_year()

    run_quarterly_gw_moe_update() >> run_daily_gw_moe()


run_quarterly_gw_moe_update = run_quarterly_gw_moe_update_dag()
