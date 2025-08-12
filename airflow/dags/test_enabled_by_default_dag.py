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
    dag_id="dag_on_by_default",
    schedule_interval="*/2 * * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["water","climate", "station_observations", "daily"],
    default_args=default_args
)
def run_xpp():

    @task(
        executor_config=executor_config_template,
        task_id="xpp_scraper"
    )
    def run_xpp_scraper(**kwargs):
        from time import sleep
        import random

        print("scraping xpp at x pp's per second")
        sleep(2)
        print("minor issue scraping xpp, only found one p")
        sleep(2)
        print("Found this many complete xpp's")
        for i in range(random.randint(0, 100)):
            print("xpp")
            sleep(2)

    run_xpp_scraper()

run_asp_scraper = run_xpp()
