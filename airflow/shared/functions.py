import os
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s
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
        """
    )


def generate_default_args(PLATFORM):
    if PLATFORM == 'OKD':
        # Use Sendgrid Backend on OKD
        return {
            'email': ['technical@foundryspatial.com'],
            'email_on_failure': True,
        }
    else:
        # Use Ches Email Service on Openshift via Callback
        return {
            'email_on_failure': False,
            'on_failure_callback': ches_failure_callback,
        }


def generate_executor_config_template(worker_size):

    POD_RESOURCES = {
        "tiny": "500Mi",
        "small": "750Mi",
        "medium": "2048Mi",
        "heavy": "4096Mi",
        "largest": "8192Mi"
    }

    resource_request = POD_RESOURCES[worker_size]

    executor_config_template = {
        "pod_override": k8s.V1Pod(
            spec=k8s.V1PodSpec(
                containers=[
                    k8s.V1Container(
                        name="base",
                        resources=k8s.V1ResourceRequirements(
                            requests=resource_request,
                            limits=resource_request
                        )
                    )
                ]
            )
        )
    }

    return executor_config_template
