from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["example"]
)
def hello_world_dag():

    @task
    def say_hello():
        print("Hello from TaskFlow!")

    say_hello()

hello_world_dag = hello_world_dag()
