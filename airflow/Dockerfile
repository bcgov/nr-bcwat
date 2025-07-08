FROM apache/airflow:2.10.5-python3.12

USER root

COPY dags/ /opt/airflow/dags/
COPY pod_templates/openshift/ /opt/airflow/pod_templates/
COPY etl_pipelines/ /opt/airflow/etl_pipelines/

RUN chown -R airflow: /opt/airflow/dags /opt/airflow/etl_pipelines

ENV PYTHONPATH = "/opt/airflow/etl_pipelines:${PYTHONPATH}"

COPY requirements.txt .

USER airflow

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install apache-airflow-providers-cncf-kubernetes apache-airflow-providers-sendgrid
