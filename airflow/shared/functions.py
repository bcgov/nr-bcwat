
from airflow.settings import AIRFLOW_HOME
from kubernetes.client import models as k8s
from shared.constants import (
    ENVIRONMENT,
    SUBJECT_TEMPLATES,
    POD_TEMPLATES
)

def generate_executor_config_template(pod_template_type):

    subject_template = SUBJECT_TEMPLATES.get(
        ENVIRONMENT,
        '/opt/airflow/email_templates/no_env_subject.html'
    )

    pod_template = POD_TEMPLATES.get(
        pod_template_type,
        "/opt/airflow/pod_templates/medium_task_template.yaml"
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
