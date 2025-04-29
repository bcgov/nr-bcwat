# Airflow

[Apache Airflow](https://airflow.apache.org/) is an open-source workflow management platform used for programmatically authoring, scheduling, and monitoring data pipelines.

To run locally, you must have docker compose installed. From the `airflow` directory, run:

```bash
docker compose build
docker compose up
```

This will initialize a metadata database, as well as initialized a scheduler, triggerer, and webserver accessible at `localhost:8080`.

In production, we are using the `KubernetesExecutor`. This does not impact running the code locally, however, you will need to assign a pod template file in the `executor_config_template`. Please reference the code below:

```bash
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
```

This way, you are able to allocate resources to worker pods to ensure each DAG has enough resources to complete.

# ETL Pipeline

The directory `etl_pipelines/` contains the scrapers that the AirFlow DAG's will be running. More documentation in the `README.md` in that directory.
