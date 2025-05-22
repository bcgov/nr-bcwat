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

default_args = {
    'email': ['technical@foundryspatial.com'],
    'email_on_failure': True
}

@dag(
    dag_id="env_hydro_dag",
    schedule_interval="0 9 * * *",
    start_date=pendulum.datetime(2025, 4, 17, tz="UTC"),
    catchup=False,
    tags=["water", "station_observations", "daily"],
    default_args=default_args
)
def run_env_hydro_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="env_hydro_scraper"
    )
    def run_env_hydro(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.env_hydro import EnvHydroPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        env_hydro = EnvHydroPipeline(date_now=logical_time, db_conn=conn)

        env_hydro.download_data()
        env_hydro.validate_downloaded_data()
        env_hydro.transform_data()
        env_hydro.check_number_of_stations_scraped()
        env_hydro.load_data()
        env_hydro.check_year_in_station_year()

    run_env_hydro()

run_env_hydro_scraper = run_env_hydro_scraper()
