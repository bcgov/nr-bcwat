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
    dag_id="weather_farm_prd_dag",
    schedule="0 8 * * *",
    start_date=datetime(2025, 5, 15),
    catchup=False,
    tags=["climate", "station_observations", "daily"],
    default_args=generate_default_args(ENVIRONMENT)
)
def run_weather_farm_prd_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
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
