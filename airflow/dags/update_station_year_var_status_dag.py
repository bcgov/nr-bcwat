import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/tiny_task_template.yaml"
    }

default_args = {
    'email': ['technical@foundryspatial.com'],
    'email_on_failure': True
}

@dag(
    dag_id="update_station_year_var_status_dag",
    schedule_interval="0 3 * * *",
    start_date=pendulum.datetime(2025, 7, 15, tz="UTC"),
    catchup=False,
    tags=["utility", "daily"],
    default_args=default_args
)
def run_update_year_var_status_dag():

    @task(
        executor_config=executor_config_template,
        task_id="variable_update"
    )
    def run_update_variable():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.utils.functions import update_station_variable_table

        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()

        update_station_variable_table(conn)

    @task(
        executor_config = executor_config_template,
        task_id="year_update"
    )
    def run_update_year():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.utils.functions import update_station_year_table

        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()

        update_station_year_table(conn)

    @task(
        executor_config = executor_config_template,
        task_id="status_update"
    )
    def run_update_station_status():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.utils.functions import update_station_status_id

        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()

        update_station_status_id(conn)

    run_update_variable() >> run_update_year() >> run_update_station_status()

run_update_year_var_status_dag = run_update_year_var_status_dag()
