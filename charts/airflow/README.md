# Deploy Via Helm

Deployments are managed for BC Water Tool Consolidation via [Helm](https://helm.sh/docs/).

To perform the following command, it is assumed you are within `./charts/airflow`.

This uses the official [apache-airflow helm chart](https://github.com/apache/airflow/blob/main/chart/README.md)

Currently, the only release that exists is on the Foundry OKD. Therefore, the only command that we run from this directory is the following:

To initialize viewing the logs within , a Persistent Volume and Storage Class MUST be initialized for the Persistent Volume Claim to be enabled.

A secret must be created in the `bcwat` namespace titled `airflow-metadata`. This holds a key value pair containing the connection information for the airflow metadata database.

This database is required for airflow, and will be populated via the migrate databases job that occurs during the helm upgrade.

```bash
apiVersion: v1
kind: Secret
metadata:
  name: airflow-metadata
  namespace: bcwat
type: Opaque
stringData:
  connection: <database connection string>
```

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow   --namespace bcwat   --create-namespace   -f values.base.yaml   -f values.okd.yaml
```

This creates a Helm release from the official `apache-airflow/airflow` Chart, where we overwrite the base airflow image with our custom airflow image.

This assumes that docker images exist for airflow and are present on the OKD internal registry.

Furthermore, this requires a Persistent Volume and Persistent Volume Claim to be initialized for logs to be collected from running pods, and be retained and able to be viewed on the webserver. To accomplish this, check the `nfs-server/README.md`
