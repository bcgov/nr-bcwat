import os
import pendulum
from airflow.decorators import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template

@dag(
    dag_id="weather_farm_prd_dag",
    schedule_interval="0 8 * * *",
    start_date=pendulum.datetime(2025, 5, 15, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "daily"],
    default_args=default_args
)
def run_weather_farm_prd_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny'),
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
