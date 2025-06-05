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

```
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m gunicorn -w 4 wsgi:app --log-level debug
```

```
cd client
npm i
npm run dev
```

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
