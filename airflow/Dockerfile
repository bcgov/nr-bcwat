FROM apache/airflow:2.10.5-python3.12

USER root

COPY dags/ /opt/airflow/dags/
COPY pod_templates/openshift/ /opt/airflow/pod_templates/
COPY email_templates/ /opt/airflow/email_templates/
COPY shared /opt/airflow/shared/
COPY etl_pipelines/ /opt/airflow/etl_pipelines/

RUN chown -R airflow: /opt/airflow/dags /opt/airflow/etl_pipelines /opt/airflow/shared

ENV PYTHONPATH = "/opt/airflow/etl_pipelines:${PYTHONPATH}"

COPY requirements.txt .

USER airflow

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r requirements.txt
RUN pip install "apache-airflow==${AIRFLOW_VERSION}" apache-airflow-providers-cncf-kubernetes apache-airflow-providers-sendgrid
