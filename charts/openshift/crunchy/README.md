# Crunchy Database Deployment

This helm chart is based upon [BCGov Crunchy Action workflow](https://github.com/bcgov/action-crunchy/tree/v1.2.0). Due to the size of our database, and the time it takes to seed said database, it does not make senes to support databases per Open PR within the Dev Namespace at this time. Therefore, we are favouring a manual approach to creating and seeding the database on our Dev/Test/Prod environments, and the steps to deploy on each environment will be listed below.

## Features

- **PostgreSQL Support** with PostGIS extensions (optional)
- **High Availability** configuration with multiple replicas
- **Backup & Recovery** options using both PVC and S3 storage
- **Monitoring Integration** with Prometheus

## Overview

The following commands assume the user is within the `charts/openshift/crunchy` directory.

These will install the required Persistent Volume Claims, Network Policies, and secrets for the Crunchy Data instance.

The Network Policies ensure that the pods assocaited with our airflow installation are capable of interacting with our database pod.

### Dev

```bash
helm upgrade --install bcwat-dev . -n cdd771-dev -f values.dev.yaml
```

### Test

```bash
helm upgrade --install bcwat-dev . -n cdd771-test -f values.test.yaml
```

### Prod

```bash
helm upgrade --install bcwat-dev . -n cdd771-prod -f values.prod.yaml
```
