# Deploy Via Helm

Deployments are managed for BC Water Tool Consolidation via [Helm](https://helm.sh/docs/).

To perform the following command, it is assumed you are within `./charts/airflow`.

This uses the official [apache-airflow helm chart](https://github.com/apache/airflow/blob/main/chart/README.md)

Currently, the only release that exists is on the Foundry OKD. Therefore, the only command that we run from this directory is the following:

To initialize viewing the logs within , a Persistent Volume and Storage Class MUST be initialized for the Persistent Volume Claim to be enabled.

A secret must be created in the `cdd771-xxx` namespace titled `bcwat-airflow-metadata`. This holds a key value pair containing the connection information for the airflow metadata database.

This database is required for airflow, and will be populated via the migrate databases job that occurs during the helm upgrade.

```bash
apiVersion: v1
kind: Secret
metadata:
  name: bcwat-airflow-metadata
  namespace: cdd771-xxx
type: Opaque
stringData:
  connection: <database connection string>
```

A secret must be created in the `cdd771-xxx` namespace titled `bcwat-airflow-fernet-key`. This holds a key value pair containing the fernet key used for encryption. It is recommended to create this key using this [Airflow Guide](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/fernet.html)

```bash
apiVersion: v1
kind: Secret
metadata:
  name: bcwat-airflow-fernet-key
  namespace: cdd771-xxx
type: Opaque
stringData:
  fernet-key: <fernet-key>
```

A secret must be created in the `cdd771-xxx` namespace titled `bcwat-flowworks-credentials`. This holds a key value pair containing the fernet key used for encryption. This value can be found on Bitwarden.

```bash
apiVersion: v1
kind: Secret
metadata:
  name: bcwat-flowworks-credentials
  namespace: cdd771-xxx
type: Opaque
stringData:
  BCWAT_FLOWWORKS_PASSWORD: <password>
  BCWAT_FLOWWORKS_USERNAME: <user>
```

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow --version 1.16.0 --namespace cdd771-dev -f values.dev.yaml
```

On Test and Production, we should be creating static webserver-secret-keys, as this is recommended for production.

```bash
apiVersion: v1
kind: Secret
metadata:
  name: bcwat-airflow-webserver-secret-key
  namespace: cdd771-xxx
type: Opaque
stringData:
  webserver-secret-key: <webserver-secret-key>
```

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow --version 1.16.0 --namespace cdd771-test -f values.test.yaml
```

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow --version 1.16.0 --namespace cdd771-prod -f values.prod.yaml
```

This creates a Helm release from the official `apache-airflow/airflow` Chart, where we overwrite the base airflow image with our custom airflow image.

This assumes that docker images exist for airflow and are present on the OKD internal registry.

Furthermore, this requires a Persistent Volume and Persistent Volume Claim to be initialized for logs to be collected from running pods, and be retained and able to be viewed on the webserver. To accomplish this, check the `nfs-server/README.md`
