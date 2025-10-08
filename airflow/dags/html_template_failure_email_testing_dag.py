import os
import pendulum
from airflow.decorators import dag, task
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

ENVIRONMENT = os.getenv('ENVIRONMENT', 'no-env-found')

# Map environments to template files
SUBJECT_TEMPLATES = {
    'OKD': '/opt/airflow/email_templates/subject/okd_subject.html',
    'PRODUCTION': '/opt/airflow/email_templates/subject/prod_subject.html',
    'TEST': '/opt/airflow/email_templates/subject/test_subject.html',
    'DEV': '/opt/airflow/email_templates/subject/dev_subject.html',
    'no-env-found': '/opt/airflow/email_templates/subject/no_env_subject.html'
}

# Get the template for this environment, with a default fallback
subject_template = SUBJECT_TEMPLATES.get(
    ENVIRONMENT,
    '/opt/airflow/email_templates/no_env_subject.html'
)

executor_config_template = {
    "pod_template_file": "/opt/airflow/pod_templates/tiny_task_template.yaml",
    "pod_override": {
        "spec": {
            "containers": [{
                "name": "base",
                "env": [
                    {
                        "name": "AIRFLOW__EMAIL__SUBJECT_TEMPLATE",
                        "value": subject_template
                    }
                ]
            }]
        }
    }
}

default_args = {
    'email': ['technical@foundryspatial.com'],
    'email_on_failure': True
}

@dag(
    dag_id="failure_email_testing",
    schedule_interval="30 * * * *",
    start_date=pendulum.datetime(2025, 5, 7, tz="UTC"),
    catchup=False,
    tags=["testing"],
    default_args=default_args
)
def trigger_failure_run():
    @task(
        executor_config=executor_config_template,
        task_id="divide_by_zero"
    )
    def trigger_failure(**kwargs):

        from etl_pipelines.utils.functions import setup_logging

        logger = setup_logging()
        logger.info("Trigger Failure - Test Email Func")
        x = 1/0
        logger.info(x)

    trigger_failure()

trigger_failure_run = trigger_failure_run()
