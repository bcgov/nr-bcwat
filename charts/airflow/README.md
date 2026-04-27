# Deploy Via Helm

Deployments are managed for BC Water Tool Consolidation via [Helm](https://helm.sh/docs/).

To perform the following command, it is assumed you are within `./charts/airflow`.

This uses the official [apache-airflow helm chart](https://github.com/apache/airflow/blob/main/chart/README.md)

Currently, the only release that exists is on the Foundry OKD. Therefore, the only command that we run from this directory is the following:

To initialize viewing the logs within , a Persistent Volume and Storage Class MUST be initialized for the Persistent Volume Claim to be enabled.

A secret must be created in the `cdd771-xxx` namespace titled `airflow-rw-db-conn`. This holds a key value pair containing the connection information for the airflow metadata database. This value can be fetched from the `uri` key on the `bcwat-test-crunchy-pguser-airflow-metadata-admin` secret.

This database is required for airflow, and will be populated via the migrate databases job that occurs during the helm upgrade.

```bash
  airflow-migrate-db-conn:
    type: Opaque
    stringData: |
      connection: {{ index ((lookup "v1" "Secret" .Release.Namespace "bcwat-test-crunchy-pguser-airflow-metadata-admin").data) "uri" | b64dec | quote }}
  airflow-rw-db-conn:
    type: Opaque
    stringData: |
      connection: {{ index ((lookup "v1" "Secret" .Release.Namespace "bcwat-test-crunchy-pguser-airflow-metadata-rw").data) "pgbouncer-uri" | b64dec | quote }}
  bcwat-airflow-rw-db-conn:
    type: Opaque
    stringData: |
      connection: {{ index ((lookup "v1" "Secret" .Release.Namespace "bcwat-test-crunchy-pguser-bcwat-airflow-read-write").data) "pgbouncer-uri" | b64dec | quote }}
```

These secrets are created at the top of the airflow values - these are used for all of the database interactions for the various microservices.

`airflow-migrate-db-conn` is the ADMIN user - and therefore cannot connect via PGBouncer, hence why it uses the uri

`airflow-rw-db-conn` uses the pgbouncer-uri, and is used for the scheduler/webserver/etc. It should be noted that permissions needed to be manually granted to this user to interact with the public schema - where all of the metadata exists regarding dag runs etc.

`bcwat-arflow-rw-db-conn` is the Connection used by the dags themselves. All of these permissions are granted in the post_import_queries.py and in the other flyway-migrations.

```bash
  psql
  \c airflow_metadata
  GRANT ALL PRIVILEGES ON DATABASE airflow_metadata TO "airflow-metadata-rw";
  GRANT ALL PRIVILEGES ON SCHEMA public TO "airflow-metadata-rw";
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "airflow-metadata-rw";
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "airflow-metadata-rw";

  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "airflow-metadata-rw";
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "airflow-metadata-rw";
```

The above permissions must be applied to each DB, either via script, or manually, for airflow services to communicate with the DB over PGBouncer.

A secret must be created in the `cdd771-xxx` namespace titled `airflow-fernet-key`. This holds a key value pair containing the fernet key used for encryption. It is recommended to create this key using this [Airflow Guide](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/fernet.html)

```bash
apiVersion: v1
kind: Secret
metadata:
  name: airflow-fernet-key
  namespace: cdd771-xxx
type: Opaque
stringData:
  fernet-key: <fernet-key>
```

A secret must be created in the `cdd771-xxx` namespace titled `airflow-flowworks-credentials`. This holds a key value pair containing the fernet key used for encryption. This value can be found on Bitwarden.

```bash
apiVersion: v1
kind: Secret
metadata:
  name: airflow-flowworks-credentials
  namespace: cdd771-xxx
type: Opaque
stringData:
  BCWAT_FLOWWORKS_PASSWORD: <password>
  BCWAT_FLOWWORKS_USERNAME: <user>
```

On Test/Production, we should be creating static webserver-secret-keys, as this is recommended for production. As per the [airflow documentation](https://airflow.apache.org/docs/helm-chart/stable/production-guide.html), this is accomplished via the below command:

```bash
python3 -c 'import secrets; print(secrets.token_hex(16))'
```

```bash
apiVersion: v1
kind: Secret
metadata:
  name: airflow-webserver-secret-key
  namespace: cdd771-xxx
type: Opaque
stringData:
  webserver-secret-key: <webserver-secret-key>
```

To perform the helm installations within each relative namespace:

```bash
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow --version 1.16.0 --namespace cdd771-dev -f values.dev.yaml
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
