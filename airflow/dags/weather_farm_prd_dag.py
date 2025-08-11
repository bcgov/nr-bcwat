import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/tiny_task_template.yaml"
    }

@dag(
    dag_id="weather_farm_prd_dag",
    schedule_interval="15 5 * * *",
    start_date=pendulum.datetime(2025, 5, 15, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "daily"]
)
def run_weather_farm_prd_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="weather_farm_prd_scraper"
    )
    def run_weather_farm_prd(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.weather_farm_prd import WeatherFarmPrdPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        weather_farm_prd = WeatherFarmPrdPipeline(date_now=logical_time, db_conn=conn)

        weather_farm_prd.download_data()
        weather_farm_prd.validate_downloaded_data()
        weather_farm_prd.transform_data()
        weather_farm_prd.load_data()
        weather_farm_prd.check_year_in_station_year()

    run_weather_farm_prd()

run_weather_farm_prd_scraper = run_weather_farm_prd_scraper()
