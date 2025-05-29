# BCWAT Archicture

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

The BC Government's BCWAT application is composed of microservices
in three groupings:

- bcwat microservices
- airflow microservices
- backend databases

The bcwat services (bcwat openshift namespace) contain:

- bcwat-nginx : Nginx wrapped application server to serve the frontend
- bcwat-api : Python API services that retrieves data from the backend

The Airflow services (airflow openshift namespace) contain:

- airflow scheduler : to schedule all data acquisition (scraper) jobs
- airflow trigger : module to run all scrapers services
- airflow webserver : user interface dashboard to all airflow services

The backend databases contain:

- bcwat PostGIS database
- bcwat PostGIS database backup (bcwat-db-repo)
- bcwat PostGIS database backup job (bcwat-db-backup)

In addition, each scraper pod scheduled by the airflow trigger will appear
in its own namespace, for example:
  drive-bc-dag-drive-bc-scraper  (pod)


![Architecture Diagram](https://github.com/bcgov/NR-BCWAT/blob/dev/documentation/BCWATArchitecture01.png?raw=true)


## bcwat-nginx

Simple Nginx service running in a container pod that serves the ViewJS
application to the users' browsers.

Build

See client/src/Dockerfile and client/src/entrypoint.sh to see how
the docker image is built.

Deployment

Two environmental variables get injected into the container at runtime.
These are:
- The base URL of the API service (VITE_BASE_API_URL)
- The mapbox token to generate mapbox maps (VITE_APP_MAPBOX_TOKEN)

Components

The frontend application (bc-wat-app) is a ViewJS (ViewJS 3.x) application
that uses the following main libraries:

- quasar
  Developer-oriented, front-end framework with VueJS components
  for best-in-class high-performance and responsive websites with good
  support for desktop and mobile browsers

- d3
  Charting library for  custom dynamic visualizations with data
  features such as selections, scales, shapes, interactions, layouts,
  geographic mapsmodule for barcharts and graphs

- mapbox
  Client-side JavaScript library for building web maps and web applications
  with user interactions that allows: 
  - Visualizing and displaying geographic data
  - Querying and filtering features on a map
  - Placing data between layers of a Mapbox style
  - Dynamically displaying and styling custom client-side data on a map
  - Data visualizations and animations
  - Adding markers and popups to maps programmatically


## bcwat-api

Python API service that provides a REST interface to the frontend application

Build

Deployment

Components

TBD - swagger API documentation


## bcwat-db

Crunchy Postgres Database with GIS extensions

Build

Deployment

Components
TBD - add DB setup, customizing and description of main stored procedures


## Airflow scrapers

Airflow is an Apache open-source platform for developing, scheduling, 
and monitoring batch-oriented workflows.

TBD - list scrappers and data sources and extra processing (maybe a table?)

## Airflow scheduler

TBD - list jobs and times and durations
TBD - section about logs and debugging

## Airflow web console

TBD - point to Airflow web console manual, maybe a screenshot?


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
