import os
from datetime import datetime
from airflow.sdk import dag, task
from shared.functions import (
    generate_default_args,
    generate_executor_config_template
)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

PLATFORM = os.getenv('PLATFORM', 'no-platform-found')

@dag(
    dag_id="intentional_failure_dag",
    schedule=None,
    start_date=datetime(2025, 4, 17),
    catchup=False,
    tags=["test", "failure"],
    default_args=generate_default_args(PLATFORM)
)
def run_intentional_failure():

    @task(
        executor_config=generate_executor_config_template('medium'),
        task_id="divide_by_zero_task"
    )
    def fail_on_purpose(**kwargs):
        result = 1 / 0
        return result

    fail_on_purpose()

run_intentional_failure = run_intentional_failure()
