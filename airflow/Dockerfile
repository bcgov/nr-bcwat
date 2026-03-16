FROM apache/airflow:3.1.7-python3.12

USER root

COPY dags/ /opt/airflow/dags/
COPY pod_templates/openshift/ /opt/airflow/pod_templates/
COPY email_templates/ /opt/airflow/email_templates/
COPY shared /opt/airflow/shared/
COPY etl_pipelines/ /opt/airflow/etl_pipelines/

RUN chown -R airflow: /opt/airflow/dags /opt/airflow/etl_pipelines /opt/airflow/shared

ENV PYTHONPATH = "/opt/airflow/etl_pipelines:${PYTHONPATH}"

COPY requirements.txt .

# Switch to airflow user for pip installations
USER airflow

# PIN AIRFLOW VERSION when installing packages
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" \
    --constraint ${HOME}/constraints.txt \
    apache-airflow-providers-cncf-kubernetes \
    apache-airflow-providers-sendgrid

RUN pip install --no-cache-dir apache-airflow-providers-fab==3.1.2

RUN pip install --no-cache-dir -r requirements.txt
