import os
from datetime import datetime
from airflow.decorators import dag, task
from kubernetes.client import models as k8s

# Executor config with a pod template file and optional override
# Does not prevent running locally
# pod_template_file handles worker pod config
executor_config_template = {
    "pod_template_file": "/opt/airflow/pod_templates/simple_task_template.yaml",
    "pod_override": k8s.V1Pod(
        metadata=k8s.V1ObjectMeta(labels={"release": "stable"})
    ),
}

@dag(
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"]
)
def k8s_hello_world_dag():

    @task(executor_config=executor_config_template)
    def say_hello():
        print("Hello from TaskFlow!")

    say_hello()

k8s_hello_world_dag = k8s_hello_world_dag()
