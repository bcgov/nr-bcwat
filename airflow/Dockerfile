FROM apache/airflow:2.10.5-python3.10

USER root

COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/
COPY pod_templates/ /opt/airflow/pod_templates/

RUN chown -R airflow: /opt/airflow/dags /opt/airflow/plugins

COPY requirements.txt .

USER airflow

RUN pip install --no-cache-dir -r requirements.txt apache-airflow-providers-cncf-kubernetes
