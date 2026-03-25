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
    dag_id="fail_on_purpose",
    schedule=None,
    start_date=datetime(2025, 5, 7),
    catchup=False,
    tags=["manual", "failing"],
    default_args=generate_default_args(ENVIRONMENT)
)
def fail_on_purpose_scraper():

    @task(
        executor_config=generate_executor_config_template('tiny', ENVIRONMENT),
        task_id="fail_on_purpose_scraper"
    )
    def fail_on_purpose(**kwargs):
        print("This DAG Fails on Purpose to test the CHES Flow...")
        x = 1/0
        print(x)

    fail_on_purpose()

fail_on_purpose_scraper = fail_on_purpose_scraper()
