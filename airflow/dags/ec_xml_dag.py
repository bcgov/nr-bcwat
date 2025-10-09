import os
import pendulum
from airflow.decorators import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template

@dag(
    dag_id="ec_xml_dag",
    schedule_interval="0 8 * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["climate", "station_observations", "daily"],
    default_args=default_args
)
def run_ec_xml_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny'),
        task_id="ec_xml_scraper"
    )
    def run_ec_xml(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.climate.ec_xml import EcXmlPipeline
        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()
        ec_xml = EcXmlPipeline(date_now=logical_time, db_conn=conn)

        ec_xml.download_data()
        ec_xml.validate_downloaded_data()
        ec_xml.transform_data()
        ec_xml.load_data()
        ec_xml.check_year_in_station_year()

    run_ec_xml()

run_ec_xml_scraper = run_ec_xml_scraper()
