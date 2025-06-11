# Airflow

[Apache Airflow](https://airflow.apache.org/) is an open-source workflow management platform used for programmatically authoring, scheduling, and monitoring data pipelines.

To run locally, create the `.env` file using the `.env.example` file. The variables that needs to be filled are located in the `BCWAT AirFlow .env` secure note on BitWarden. After that, you must have docker compose installed. From the `airflow` directory, run:

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

## ETL Pipeline

The directory `etl_pipelines/` contains the scrapers that the AirFlow DAG's will be running. More documentation in the `README.md` in that directory.

### DAGs

The DAGs that will be running are located in the `dags/` directory. They will have a singular task that will run the required steps for each scraper. The general strucutre will be as follows:

```python
scraper = SomeScraperClass(db_conn, datetime)

scraper.download_data()
scraper.validate_data()
scraper.transform_data()
scraper.check_number_of_stations_scraped()
scraper.load_data()
scraper.check_year_in_station_year()
```

The `download_data` method will download the file that the scraper is pointed to.

`validate_data` will validate the data types of each column, and that the column names are correct.

`transform_data` will apply the required transformations for the data that was downloaded so that it can be inserted in to the database.

`check_number_of_stations_scraped` will check how many unqiue station_id's are left in the transformed data. If the ratio of stations left in the transformed data and total stations in the network is less than a certain ratio, it will log an `Warning` and continue.

`load_data` will insert the data into the database.

`check_year_in_station_year` will check if the current year is in the `station_year` table. If it is not, then it will insert the current year into the table.

The `check` methods do not exist for the `DataBcPipeline` class DAGs.

#### Notable DAGs

The [`wra_wrl_dag.py`](/airflow/dags/wra_wrl_dag.py) is the DAG that will be running the `water_rights_applications_public.py`, and `water_rights_licences_public.py` scrapers. This DAG will orchestrate both scrapers because the table that they will serve the frontend is the same tables, thus, if one scraper truncated the table being accessed by the frontend, the other scrapers data will be affected, which will cause the frontend to be missing some data. This is avoided by having each scraper scrape in to separate tables, then calling an function that will merge the two tables into one.

As a consequence, this DAG will have three tasks in total:

1. Run `water_rights_applications_public.py`
2. Run `water_rights_licences_public.py`
3. Merge the two tables into one

With the dependencies of the tasks determined by:
```
[run_wra(), run_wrl()] >> run_combine()
```
The dependencies are represented by the `>>` notation, where this inidicates that the tasks to the left must finish before the task on the right can be started. The `trigger_rule="all_success"` argument in the `@task` decorator for `run_combine` makes it so that both tasks, `run_wra()`, and `run_wrl()` must succeed before `run_combine` can be run.

## Running on Production

Via the webserver URL, connections must be made for the target postgres database (currently `bcwat-dev`), as well as for the email client (`sendgrid_default`)
