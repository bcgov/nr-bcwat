# Disaster Recovery

This document serves to outline how to recover our Openshift Dev/Test/Production namespaces in the instance of a major outage, with an emphasis on restoring Production.

## Services

There are 4 Major Services for BCWAT:

- API
- Airflow Scrapers
  - Scheduler
  - Triggerer
  - Webserver
- API
- Crunchy Database
  - PGBouncer
  - PGBackRest (Prod Only)
- Frontend

The most critical service is the database. An unhealthy database means every other aspect of the application cannot function properly. Therefore, Github Actions have been built to recreate and seed a database on each environment using the latest full backup available on S3. As requested by the BCGov, we are only performing backups for our Production Database. This means that in the case of Dev/Test databases going down, they will be restored using the latest backup of Prod.

Due to the nature of our application, this is a none issue. All of our databases should effectively be 1:1, as the only way data gets inserted or updated within each database is via scrapping from the same data sources.

Rebuilding any component outside of the database is extremely straightforwards and will be explored within the following sections. The section below outlines how to trigger a DB Rebuild with the latest available data.

## Github Actions

### Database

Each Github Action used for Disaster Recovery is prepended by `disaster-recovery-`. These include:

- `disaster-recovery-dev-deploy-seed-db.yml`
- `disaster-recovery-test-deploy-seed-db.yml`
- `disaster-recovery-prod-deploy-seed-db.yml`

As mentioned above, each of these jobs will recreate the database on the specified environment by cloning the latest production backup on S3.

This should only be ran in the most dire of situations.

### Deployments

#### Production

Once the database is up and running, kicking off a manual Production deploy via `prod-deploy.yml` should recreate our Airflow instance, alongside our Frontend/API production builds. These deployments will be built from the latest code deployed on `main` branch.

#### Dev/Test

There are not explicit actions that exist to manually kick off a deploy for Dev/Test. To accomplish this, one must create a PR targetting main. This will create a new Frontend/API deployment that uses the Dev database. Once this PR is approved, merging into `main` will first trigger a rebuild of the `airflow` instance on the dev environment, before building the `airflow` instance on the test environment, and then deploying the Frontend/API to `test`.
