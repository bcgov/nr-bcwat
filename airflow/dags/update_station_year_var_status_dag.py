import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.constants import default_args
from shared.functions import generate_executor_config_template
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

@dag(
    dag_id="update_station_year_var_status_dag",
    schedule="30 13 * * *",
    start_date=datetime(2025, 7, 15),
    catchup=False,
    tags=["utility", "daily"],
    default_args=default_args
)
def run_update_year_var_status_dag():

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
        task_id="variable_update"
    )
    def run_update_variable():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.utils.functions import update_station_variable_table

        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()

        update_station_variable_table(conn)

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
        task_id="year_update"
    )
    def run_update_year():
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        from etl_pipelines.utils.functions import update_station_year_table

        hook = PostgresHook(postgres_conn_id="bcwat_db")
        conn = hook.get_conn()

        update_station_year_table(conn)

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
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
