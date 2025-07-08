import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s

executor_config_template = {
    "pod_template_file": "/opt/airflow/pod_templates/simple_task_template.yaml"
}

@dag(
    dag_id="hello_world",
    schedule_interval="30 * * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["hello_world"]
)
def hello_world():

    @task(
        executor_config=executor_config_template,
        task_id="hello_world"
    )
    def run_hello_world(**kwargs):

        print(f"Hello World!!!")

    run_hello_world()

hello_world = hello_world()
