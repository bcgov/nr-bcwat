FROM apache/airflow:2.10.5-python3.10

USER root

COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
COPY pod_templates/ /opt/airflow/pod_templates/
COPY etl_pipelines/ /opt/airflow/etl_pipelines/

RUN chown -R airflow: /opt/airflow/dags /opt/airflow/plugins /opt/airflow/etl_pipelines

ENV PYTHONPATH = "/opt/airflow/etl_pipelines:${PYTHONPATH}"

COPY requirements.txt .

USER airflow

RUN pip install --no-cache-dir -r requirements.txt apache-airflow-providers-cncf-kubernetes
