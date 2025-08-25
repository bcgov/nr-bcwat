# BC Water Consolidation Tool

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Maturing-007EC6)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)

![Tests](https://github.com/bcgov/vue3-scaffold/workflows/Tests/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/c8851505a24845123966/maintainability)](https://codeclimate.com/github/bcgov/vue3-scaffold/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/c8851505a24845123966/test_coverage)](https://codeclimate.com/github/bcgov/vue3-scaffold/test_coverage)

A clean Vue 3 frontend & backend scaffold example

To learn more about the **Common Services** available visit the [Common Services Showcase](https://bcgov.github.io/common-service-showcase/) page.

## Directory Structure

```txt
.github/                        - PR, Issue templates
.vscode/                        - VSCode environment configurations
airflow/                        - Apache Airflow deployment for orchestrating data pipelines
├── config/                     - Configuration files used by DAGs or Airflow runtime
├── dags/                       - DAG definitions that specify workflows and task dependencies
├── etl_pipelines/              - Reusable ETL components or modular pipeline logic imported by DAGs
├── logs/                       - Local directory for Airflow logs (mounted in docker-compose)
├── plugins/                    - Custom Airflow plugins (operators, sensors, hooks, etc.)
├── pod_templates/              - KubernetesPodOperator YAML templates for task execution in K8s
backend/                        - Flask API
├── database_initialization/    - Scripts and assets for initializing the application database
├── tests/                      - Unit Tests for Backend (PyTest)
charts/                         - Helm charts for Managed Kubernetes Clusters
├── okd/                        - Helm charts/values and overrides specific to OKD environment
├── openshift/                  - Helm charts/values and overrides specific to OpenShift deployments
client/                         - Vue Application
├── cypress/                    - Cypress E2E & Component testing configuration and specs
├── public/                     - Static public assets served as-is (e.g., index.html, icons)
├── src/                        - Frontend source code including components, views, and logic
documentation/                  - Markdown or static documentation content for the project
migrations/                     - Database schema versioning and migration scripts
├── sql/                        - SQL-based migration files for Flyway
tests/                          - Top-level tests for full-system or multi-component scenarios
├── integration/                - Integration tests spanning multiple services
├── load/                       - Load or performance testing scripts and configs
_config.yml                     - Configuration file for static site generators (e.g., Jekyll/GitHub Pages)
.codeclimate.yml                - CodeClimate analysis configuration
.dockerignore                   - Docker ignore file to exclude files from Docker builds
.editorconfig                   - Editor configuration for consistent coding styles
.gitattributes                  - Git settings for line endings, linguist overrides, etc.
.gitignore                      - Git ignore file to exclude files from version control
CODE-OF-CONDUCT.md              - Code of conduct for contributors
COMPLIANCE.yaml                 - BCGov PIA/STRA compliance status and tracking
CONTRIBUTING.md                 - Contribution guidelines for the project
docker-compose.yaml             - Multi-service container orchestration config for local dev/testing of Client/Backend
LICENSE                         - Primary software license (Apache)
LICENSE.md                      - Alternate or human-readable license reference
SECURITY.md                     - Security policy and vulnerability reporting instructions
```

## Documentation

- [Application Readme](frontend/README.md)
- [Architecture](documentation/Architecture.md)
- [Product Roadmap](https://github.com/bcgov/vue3-scaffold/wiki/Product-Roadmap)
- [Product Wiki](https://github.com/bcgov/vue3-scaffold/wiki)
- [Security Reporting](SECURITY.md)

## Quick Start Dev Guide

You can quickly run this application in development mode after cloning by opening two terminal windows and running the following commands (assuming you have already set up local configuration as well). Refer to the [Backend Readme](backend/README.md) and [Frontend Readme](client/README.md) for more details. Please ensure you have [python 3.12](https://www.python.org/downloads/) and [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) installed.

```bash
cd backend
chmod +777 ./startup.sh
./startup.sh
```

```bash
cd client
npm i
npm run dev
```

## CI/CD

To perform operations in specific namespaces, we MUST initialize a storage account and use that token to authenticate. This is created via the following command on Openshift. This is the OC_TOKEN Value.

```bash
apiVersion: v1
kind: Secret
metadata:
    name: pipeline-token-gha
    namespace: <your-namespace>
    annotations:
        kubernetes.io/service-account.name: "pipeline"
type: kubernetes.io/service-account-token
```

We must add the proper permissions onto the pieline service account:

```bash
oc adm policy add-role-to-user admin -z pipeline -n <your-namespace>
```

We then get the value, which we copy into github secrets (environment specific) via:

```bash
oc get secret pipeline-token-gha -n xxx -o jsonpath='{.data.token}' | base64 -d
```

We use environment specific github secrets - this is dictated by the environment key within some of our actions (see merge.yml)

```bash
  deploy-test:
    name: Deploy (TEST)
    uses: ./.github/workflows/.deployer.yml
    secrets: inherit
    with:
      environment: TEST
      db_user: app
      tag: ${{ inputs.tag }}
```

This means that the `OC_TOKEN/OC_NAMESPACE` values used within `deployer.yml` will correspond to those declared in the `TEST` Environment.

## August 15-31st: Mitigations

While UAT is occurring, the main DevOps engineer is out of office. This portion of the document serves to detail all mitigation techniques for all potential issues. A future goal is to fully automate each aspect of the deployment, however we are not at that stage. For issues regarding airflow deployments and database deployments, there will be things that need to be manually applied to the openshift cluster after authenticating in the CLI. These are all included within the READMEs within the `charts` subdirectory.

For any major concerns, please message Liam on mattermost, and we can debug together. I hope the guide below is unused, however it is necessary to include and detail the steps.

### Database Backup/Restore

The biggest issue would be any of the databases getting knocked down. If this occurs, all of the airflow scrapers will get stuck in crash loops, and the API will be stuck hanging as it will be unable to validate a DB connection. In this instance, I would recommend tearing everything down via helm uninstall commands. This is the worst case scenario, and highly unlikely as we they have been stable for some time.

To reinitialize a database, all that needs to be ran is the `helm install` command for the specific namespace. These commands can be found within `charts/openshift/crunchy/README.md`.

Once this occurs, we can reinitialize the database using a dump file. In the future, we can restore said database from the production restore path, as we do not have backups running on dev/test as this is unnecessary.

Currently, we have manual backup/restore scripts. These are how we initialized the test/prod databases.

#### Backup - Update Image

If any code changes have been made to `backup_and_restore_database/backup_database/backup_and_upload_to_s3.py`, you will need to rebuild the image our Kubernetes Job will use.

To do this, you can kick off the github action `build-push-dump-db.yaml` via workflow dispatch and selecting the branch you want to build from, or uncommenting the `push` block and updating the branch name to be the branch you want to build from.

```bash
name: "Build & Push backup to s3"

on:
  # push:
  #   branches:
  #     - <database-backup-brach>
  workflow_dispatch:
```

This will update the `latest` tag on the image we use in the `backup.yaml` file mentioned below.

#### Perform Backup

To create a backup from a specific database, look at the files within `charts/openshift/backup-db`.

NOTE: `<ENVIRONMENT>` refers to `dev/test/prod` - and is dependent on the environment you wish to backup from. All of the environments should be 1:1 in terms of DB content due to the nature of this tool.

Firstly, ensure the network policy exists on the specified namespace to allow communication with the database. You can check this by running:

```bash
oc get networkpolicy -n cdd771-<ENVIRONMENT>
```

If no network policy exists `backup-to-db` for said namespace, update `knp.yaml` to reference the proper database:

```bash
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backup-to-db
spec:
  podSelector:
    matchLabels:
      postgres-operator.crunchydata.com/cluster: bcwat-<ENVIRONMENT>-crunchy
```

Apply via navigating to `charts/openshift/backup-db`:

```bash
oc apply -f knp.yaml
```

Within `backup.yaml` You will need to edit the namespace/secrets to correspond to the environment you are backing up to s3 from:

```bash
metadata:
  name: backup-crunchy-into-s3
  namespace: cdd771-<ENVIRONMENT>

env:
  env:
    - name: DB_HOST
      valueFrom:
        secretKeyRef:
          name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
          key: host
    - name: DB_PORT
      valueFrom:
        secretKeyRef:
          name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
          key: port
    - name: DB_NAME
      valueFrom:
        secretKeyRef:
          name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
          key: dbname
    - name: DB_USER
      valueFrom:
        secretKeyRef:
          name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
          key: user
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
          key: password
    - name: AWS_ACCESS_KEY_ID
      valueFrom:
        secretKeyRef:
          name: s3-secrets
          key: ACCESS_KEY
    - name: AWS_SECRET_ACCESS_KEY
      valueFrom:
        secretKeyRef:
          name: s3-secrets
          key: SECRET_KEY
    - name: BUCKET_NAME
      valueFrom:
        secretKeyRef:
          name: s3-secrets
          key: BUCKET_NAME
    - name: AWS_ENDPOINT_URL
      valueFrom:
        secretKeyRef:
          name: s3-secrets
          key: ENDPOINT_URL

```

ALL of the secrets required exist on all namespaces.

### Database Restore

Performing a restore follows the same lines as performing the backup.

The only differences are that you will be navigating to the namespace with the database you wish to restore, rather than the database you backed up from, and you have an extra environment variable to update in the `charts/openshift/crunchy/restore-db/restore.yaml` file - the BACKUP_FILE (correspond to the date of the backup you made)

#### Restore - Update Image

If any code changes have been made to `backup_and_restore_database/backup_database/backup_and_upload_to_s3.py`, you will need to rebuild the image our Kubernetes Job will use.

To do this, you can kick off the github action `build-push-restore-db.yaml` via workflow dispatch and selecting the branch you want to build from, or uncommenting the `push` block and updating the branch name to be the branch you want to build from.

```bash
name: "Build & Push Restore from S3"

on:
  # push:
  #   branches:
  #     - <database-restore-branch>
  workflow_dispatch:
```

This will update the `latest` tag on the image we use in the `restore.yaml` file mentioned below.

#### Perform Restore

To restore to your specified database, look at the files within `charts/openshift/restore-db`.

NOTE: `<ENVIRONMENT>` refers to `dev/test/prod` - and is dependent on the environment you wish to restore to.

Firstly, ensure the network policy exists on the specified namespace to allow communication with the database. You can check this by running:

```bash
oc get networkpolicy -n cdd771-<ENVIRONMENT>
```

If no network policy exists `restore-to-db` for said namespace, update `knp.yaml` to reference the proper database:

```bash
metadata:
  name: restore-to-db
spec:
  podSelector:
    matchLabels:
      postgres-operator.crunchydata.com/cluster: bcwat-<ENVIRONMENT>-crunchy
```

Apply via navigating to `charts/openshift/restore-db`:

```bash
oc apply -f knp.yaml
```

Within `restore.yaml` You will need to edit the namespace/secrets to correspond to the environment you are backing up to s3 from:

```bash
apiVersion: batch/v1
kind: Job
metadata:
  name: restore-crunchy-from-s3
  namespace: cdd771-<ENVIRONMENT>
spec:
  backoffLimit: 0
  template:
    metadata:
      labels:
        role: restore-db
    spec:
      restartPolicy: Never
      containers:
        - name: restore-from-s3
          image: ghcr.io/bcgov/nr-bcwat/backup_and_restore_database/restore_database:latest
          imagePullPolicy: Always
          env:
            - name: DB_HOST
              valueFrom:
                secretKeyRef:
                  name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
                  key: host
            - name: DB_PORT
              valueFrom:
                secretKeyRef:
                  name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
                  key: port
            - name: DB_NAME
              valueFrom:
                secretKeyRef:
                  name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
                  key: dbname
            - name: DB_USER
              valueFrom:
                secretKeyRef:
                  name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
                  key: user
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: bcwat-<ENVIRONMENT>-crunchy-pguser-bcwat-api-admin
                  key: password
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: s3-secrets
                  key: ACCESS_KEY
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: s3-secrets
                  key: SECRET_KEY
            - name: BUCKET_NAME
              valueFrom:
                secretKeyRef:
                  name: s3-secrets
                  key: BUCKET_NAME
            - name: AWS_ENDPOINT_URL
              valueFrom:
                secretKeyRef:
                  name: s3-secrets
                  key: ENDPOINT_URL
            - name: BACKUP_FILE
              value: <DUMP FILE CREATED VIA BACKUP>

```

ALL of the secrets required exist on all namespaces.

To verify the backup file, it is logged at the end of the backup script.

### Airflow Creation

Airflow Creation is trivial. If it gets knocked down, the secrets that we have created will persist unless manually deleted. Do not delete these secrets. If they do get deleted, the instructions to create them are included within the `charts/openshift/airflow/README.md`.

Furthermore, airflow can get fully configured by the `merge.yml` action, as it will deploy the latest version of the scrapers to all openshift environments. It will also handle secret creation on openshift due to the secrets being created for each environment on github.

Running the helm installation commands for any of the namespaces will also work. The only thing not handled by CI/CD is the creation of the `airflow-data` PVC - this can be manually applied.

The yaml for this can be found within `airflow/pvc_templates/openshift/airflow_data_pvc.yaml`

```bash
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: airflow-data
  namespace: cdd771-<ENVIRONMENT>
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 15Gi
  storageClassName: netapp-file-standard
  volumeMode: Filesystem
```

You can manually apply this via:

```bash
oc apply -f airflow_data_pvc.yaml
```

This will create the PVC, which will ensure the quarterly scrapers can access the PVC.

### Frontend/API

The API/Frontend images are not created manually and are seamlessly handled via our CI/CD.

To deploy to the dev deployment, create a pull request targetting main.

To create a test deployment, merge that pull request into main.

We do not currently have the prod deployment enabled, and this will be done when I am back to office. To handle this, it should be as simple as uncommenting the `deploy-prod` block within `merge.yml`. This will trigger the deployments as adhering to the QSOS guide.

The actions used on PR Creation/Merge to main create the network policies and secrets as used by our deployments, and we have had no issues with them thus far.

## Getting Help or Reporting an Issue

To report bugs/issues/features requests, please file an [issue](https://github.com/bcgov/vue3-scaffold/issues).

## How to Contribute

If you would like to contribute, please see our [contributing](CONTRIBUTING.md) guidelines.

Please note that this project is released with a [Contributor Code of Conduct](CODE-OF-CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

```txt
Copyright 2022 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
