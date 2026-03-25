from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s
from shared.constants import (
    SUBJECT_TEMPLATES,
    POD_TEMPLATES
)
from ches_client.ches_client import CHESClient


def ches_failure_callback(context):

    ti = context.get("ti")
    exception = context.get("exception")

    client = CHESClient()
    client.send_email(
        subject=f"{ti.dag_id} {ti.state}",
        body=f"""
            Try {ti.try_number} out of {ti.max_tries + 1}<br>
            DAG/TASK/RUN: {ti.dag_id} / {ti.task_id} / {ti.run_id}<br>
            Exception:<br>{exception}<br>
            View Logs: <a href="{ti.log_url}">{ti.log_url}</a><br>
            You can access the logs above by authenticating to the BCGov Openshift via CLI,
            and navigating to the namespace specified in the email subject line.<br>
            To be able to click on the log_url below, you must port-forward the airflow
            webserver pod to your localhost:8080, and then authenticate using the default
            Airflow credentials.<br>
            oc port-forward airflow-webserver-xxx 8080:8080<br>
        """
    )


def generate_default_args(ENVIRONMENT):
    if ENVIRONMENT == 'OKD':
        # Use Sendgrid Backend on OKD
        return {
            'email': ['technical@foundryspatial.com'],
            'email_on_failure': True,
        }
    else:
        # Use Ches Email Service on OKD via Callback
        return {
            'email_on_failure': False,
            'on_failure_callback': ches_failure_callback,
        }


def generate_executor_config_template(pod_template_type, ENVIRONMENT):
    pod_template = POD_TEMPLATES.get(
        pod_template_type,
        "/opt/airflow/pod_templates/medium_task_template.yaml"
    )

    subject_template = SUBJECT_TEMPLATES.get(
        ENVIRONMENT,
        '/opt/airflow/email_templates/no_env_subject.html'
    )

    executor_config_template = {
        "pod_template_file": pod_template,
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                containers=[
                    k8s.V1Container(
                        name="base",
                        env=[k8s.V1EnvVar(name="AIRFLOW__EMAIL__SUBJECT_TEMPLATE", value=subject_template)]
                    )
                ]
            )
        )
    }

    return executor_config_template
