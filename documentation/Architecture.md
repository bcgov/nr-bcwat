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
- bcwat PostGIS database backup
- bcwat PostGIS database image repository

In addition, each scraper pod scheduled by the airflow trigger will appear
in its own namespace, for example:
  drive-bc-dag-drive-bc-scraper  (pod)


![Architecture Diagram](https://github.com/bcgov/NR-BCWAT/documentation/BCWATArchitecture01.png?raw=true)


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
