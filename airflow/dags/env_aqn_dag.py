import os
import pendulum
from airflow.decorators import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template

@dag(
    dag_id="env_aqn_dag",
    schedule_interval="0 8 * * *",
    start_date=pendulum.datetime(2025, 5, 15, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "daily"],
    default_args=default_args
)
def run_env_aqn_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny'),
        task_id="env_aqn_scraper"
    )
    def run_env_aqn(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.env_aqn import EnvAqnPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        env_aqn = EnvAqnPipeline(date_now=logical_time, db_conn=conn)

        env_aqn.download_data()
        env_aqn.validate_downloaded_data()
        env_aqn.transform_data()
        env_aqn.load_data()
        env_aqn.check_year_in_station_year()

    run_env_aqn()

run_env_aqn_scraper = run_env_aqn_scraper()
