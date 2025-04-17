# Deploy Via Helm

Deployments are managed for BC Water Tool Consolidation via [Helm](https://helm.sh/docs/).

To perform the following command, it is assumed you are within `./charts/airflow`.

Currently, the only release that exists is on the Foundry OKD. Therefore, the only command that we run from this directory is the following:

To initialize viewing the logs within , a Persistent Volume and Storage Class MUST be initialized for the Persistent Volume Claim to be enabled.

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow   --namespace bcwat   --create-namespace   -f values.base.yaml   -f values.okd.yaml
```

This creates a Helm release from the official `apache-airflow/airflow` Chart, where we overwrite the base airflow image with our custom airflow image.

This assumes that docker images exist for airflow and are present on the OKD internal registry.
