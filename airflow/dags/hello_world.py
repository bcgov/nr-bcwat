import os
import pendulum
from airflow.decorators import dag, task
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

environment = os.getenv("AIRFLOW_ENVIRONMENT")
print(environment)

if environment == "okd":
    executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/okd/medium_task_template.yaml"
    }
elif environment =="openshift":
    executor_config_template = {
        "pod_template_file": "/opt/airflow/pod_templates/openshift/medium_task_template.yaml"
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

        print(f"Hello World: Running in Environment: {environment}")


    run_hello_world()

hello_world = hello_world()
