import os
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

POD_TEMPLATES = {
    "tiny": "/opt/airflow/pod_templates/tiny_task_template.yaml",
    "small": "/opt/airflow/pod_templates/small_task_template.yaml",
    "medium": "/opt/airflow/pod_templates/medium_task_template.yaml",
    "largest": "/opt/airflow/pod_templates/largest_task_template.yaml",
    "heavy": "/opt/airflow/pod_templates/heavy_task_template.yaml"
}

default_args = {
    'email': ['technical@foundryspatial.com'],
    'email_on_failure': True
}
