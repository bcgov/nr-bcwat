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
    dag_id="wsc_hydro_dag",
    schedule_interval="0 8 * * *",
    start_date=pendulum.datetime(2025, 4, 17, tz="UTC"),
    catchup=False,
    tags=["water", "station_observations", "daily"]
)
def run_wsc_hydro_scraper():

    @task(
        executor_config=executor_config_template,
        task_id="wsc_hydro_scraper"
    )
    def run_wsc_hydro(**kwargs):
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.scrapers.StationObservationPipeline.water.wsc_hydrometric import WscHydrometricPipeline


        logical_time = kwargs["logical_date"]
        hook = PostgresHook(postgres_conn_id="bcwat-dev")
        conn = hook.get_conn()
        wsc_hydro = WscHydrometricPipeline(date_now=logical_time, db_conn=conn)

        wsc_hydro.download_data()
        wsc_hydro.validate_downloaded_data()
        wsc_hydro.transform_data()
        wsc_hydro.load_data()



    run_wsc_hydro()

run_wsc_hydro_scraper = run_wsc_hydro_scraper()
