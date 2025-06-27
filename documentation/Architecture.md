# BCWAT Architecture

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

The BC Government's BCWAT application is composed of microservices
in three groupings:

- bcwat microservices
- airflow microservices
- backend databases

The bcwat services (bcwat openshift helm target) contain:

- bcwat-nginx : Nginx wrapped application server to serve the frontend
- bcwat-api : Python API services that retrieves data from the backend

The Airflow services (airflow openshift helm target) contain:

- airflow scheduler : to schedule all data acquisition (scraper) jobs
- airflow trigger : module to run all scrapers jobs
- airflow webserver : user interface dashboard to monitor scrapers

The backend databases contain:

- bcwat PostGIS database
- bcwat PostGIS database backup (bcwat-db-repo)
- bcwat PostGIS database backup job (bcwat-db-backup)

In addition, each scraper pod scheduled by the airflow trigger will appear
as a deployed pod, for example:
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

- quasar : Developer-oriented, front-end framework with VueJS components
  for best-in-class high-performance and responsive websites with good
  support for desktop and mobile browsers

- d3 : Charting library for  custom dynamic visualizations with data
  features such as selections, scales, shapes, interactions, layouts,
  geographic mapsmodule for barcharts and graphs

- mapbox : Client-side JavaScript library for building web maps and
  web applications with user interactions that allows:
  - Visualizing and displaying geographic data
  - Querying and filtering features on a map
  - Placing data between layers of a Mapbox style
  - Dynamically displaying and styling custom client-side data on a map
  - Data visualizations and animations
  - Adding markers and popups to maps programmatically


## bcwat-api

Python API service that provides a REST interface to the frontend application

To start the API, first create a venv:

`cd backend`
`python3 -m venv /path/to/venv/directory`
`source /path/to/venv/directory/bin/activate`
`pip install -r requirements.txt`

Start the API by running the startup script: 
`cd backend`
`chmod +777 ./startup.sh`
`./startup.sh`

Swagger documentation can be found at port 8000 at `/docs` and conform to [OpenAPI Specification 3.0](https://swagger.io/specification/).
Routes can be tested by expanding the relevant endpoint name and method, and clicking 'Try it out'. A response body containing the 
structure of the json will be displayed. This format is used to populate various components on the front end. 


## bcwat-db

Crunchy Postgres Database with GIS extensions

Build

Deployment

Components

The data base will consist of 3 schemas, `bcwat_lic`, `bcwat_obs`, and `bcwat_ws`. The first will store the information on water licensing data, the second will store the information on water and climate observation collected from stations throught BC, and the last will store the information on watersheds, such as their land cover, water use, etc.

Once a database has been created, it can be populated with the schemas, and all the data that needs to be populated before it can be scraped into. The associated documentation and scripts are located in the [database_initialization README](https://github.com/bcgov/NR-BCWAT/tree/dev/backend/database_initialization/README.md).


## Airflow scrapers

Airflow is an Apache open-source platform for developing, scheduling,
and monitoring batch-oriented workflows.

Each scraper gets it's own Directed Acyclic Graph (DAG) file in AirFlow. The DAG files are located in the [`airflow/dags`](https://github.com/bcgov/NR-BCWAT/tree/dev/airflow/dags) directory. Each DAG file is a Python file that contains the definition of the workflow, they can have multiple tasks, but since scraping tasks not complex, it has been combined in to one task, so that there is no intermediate data storing required.For a more detailed description of the DAG files, see the AirFlow documentation in the [airflow README](https://github.com/bcgov/NR-BCWAT/tree/dev/airflow/README.md).

The following table has the DAG ID, the source that it is scraping from, the description of the data that it is scraping, and the variables that it is scraping.

| DAG ID | Source | Description | Variables |
| --- | --- | --- | --- |
| `asp_dag` | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/) | Automated Snow Pillow (ASP) data from automated stations.| <ul><li>Temperature</li><li>Precipitation</li><li>Snow Depth</li><li>Snow Water Equivalent (SWE)</li></ul> |
| `drive_bc_dag` | [Drive BC](http://www.drivebc.ca/) | The only scraper that runs hourly. Collects data from the DriveBC API. The hourly data is converted in to daily data once a day. | <ul><li>Snow Depth</li><li>Temperature</li><li>Precipitation Amount</li><li>Hourly Precipitation</li></ul>
| `ec_xml_dag` | [MSC Data Mart](https://dd.meteo.gc.ca/) | MSC Data Mart XML Scraper. | <ul><li>Temperature</li><li>Precipitation</li><li>Wind</li><li>Snow Amount</li></ul> |
| `env_aqn` | [BC Ministry of Environment](https://www.env.gov.bc.ca/epd/bcairquality/aqo/csv/Hourly_Raw_Air_Data/Meteorological/) | Data from the Ministry of Environment. This data originally came from PCIC. | <ul><li>Temperature</li><li>Precipitation</li></ul> |
| `env_hydro_dag` | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/water/) | Water stage and discharge from BC Government. | <ul><li>Discharge</li><li>Level</li></ul> |
| `flnro_wmb_dag` | [BC Ministry of Forest](https://www.for.gov.bc.ca/ftp/HPR/external/!publish/BCWS_DATA_MART/) | FLNRO-WMB data from the Ministry of Forest. Was originally from PCIC data porta. | <ul><li>Temperature</li><li>Precipitation</li></ul> |
| `flowworks_dag` | Data from FlowWorks API | The access to the FlowWorks API requires an bearer token. | <ul><li>Temperature</li><li>Precipitation</li><li>Dischage</li><li>Level</li><li>Snow Water Equivalent</li><li>Rainfall</li></ul> |
| `gw_moe_dag` | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/) | Groundwater data from the Ministry of Environment. | <ul><li>Groundwater Level</li></ul> |
| `msp_dag` | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/) | Manual Snow Pillow data from the Ministry of Environment. | <ul><li>Snow Depth</li><li>Snow Water Equivalent</li><li>Percent Density</li></ul> |
| `water_licences_bcer_dag` | BC-ER ArcGIS Layer | Data from an ArcGIS data layer | <ul><li>Short Term Approvals</li></ul> |
| `weather_farm_prd_dag` | [BC Peace River Regional District Data](http://www.bcpeaceweather.com/api/WeatherStation/) | Data From BC Peace River Regional District weather stations. Some of the stations are not returning data but some of them work. | <ul><li>Temperature</li><li>Rainfall</li></ul> |
| `wls_water_approval_dag` | [DataBC Data Catalogue](https://catalogue.data.gov.bc.ca/) | Data from DataBC scraped using the `bcdata` Python package. This scraper scrapes the Water Rights Approval Points | <ul><li>Water Rights Approval Points</li></ul> |
| `wls_wra_dag` | [DataBC Data Catalogue](https://catalogue.data.gov.bc.ca/) | Data from DataBC scraped using the `bcdata` Python package. This scraper scrapes the Public Water Rights Applications | <ul><li>Public Water Rights Applications</li></ul> |
| `wls_wrl_dag` | [DataBC Data Catalogue](https://catalogue.data.gov.bc.ca/) | Data from DataBC scraped using the `bcdata` Python package. This scraper scrapes the Public Water Rights Licences | <ul><li>Public Water Rights Licences</li></ul> |

Following are the quarterly scrapers that should be run when the new Hydat version is available:

| DAG ID | Source | Description | Variables |
| --- | --- | --- | --- |
| `quarterly_climate_ec_update_dag` | [MSC Data Mart](https://dd.meteo.gc.ca/) | BC Climate daily data from MSC Data Mart |  <ul><li>Temperature</li><li>Precipitation</li><li>Snow Depth</li><li>Snow Amount</li></ul>  |
| `quarterly_gw_moe_dag` | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/) | Groundwater data from the Ministry of Environment. Similar source to the daily `gw_moe` scraper, but this takes the average .csv file. | <ul><li>Groundwater Level</li></ul> |
| `quarterly_hydat_import_dag` | [Hydat](https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/) | Hydat database which comes in a `.zip` format. Must be decompressed to be accessed. | <ul><li>Water Discharge</li><li>Water Level</li></ul> |
| `quarterly_water_quality_eccc_dag` | [ECCC Data Catalogue](https://data-donnees.az.ec.gc.ca/) | Water quality data from various locations. Gathered via the ECCC Data Catalogue API. | <ul><li>Water Quality</li></ul> |

## Airflow scheduler

The schedule for each scraper is listed below:

| DAG ID | Run Time (UTC) | Frequency |
| --- | --- | --- |
| `asp_dag` | `TBD` | Daily |
| `drive_bc_dag` | Every hour on the 30th minute | Hourly |
| `ec_xml_dag` | `TBD` | Daily |
| `env_aqn` | `TBD` | Daily |
| `env_hydro_dag` | `TBD` | Daily |
| `flnro_wmb_dag` | `TBD` | Daily |
| `flowworks_dag` | `TBD` | Daily |
| `gw_moe_dag` | `TBD` | Daily |
| `msp_dag` | `TBD` | Daily |
| `water_licences_bcer_dag` | `TBD` | Daily |
| `weather_farm_prd_dag` | `TBD` | Daily |
| `wls_water_approval_dag` | `TBD` | Daily |
| `wls_wra_dag` | `TBD` | Daily |
| `wls_wrl_dag` | `TBD` | Daily |
| `quarterly_climate_ec_update_dag` | `TBD` | Quarterly |
| `quarterly_gw_moe_dag` | `TBD` | Quarterly |
| `quarterly_hydat_import_dag` | `TBD` | Quarterly |
| `quarterly_water_quality_eccc_dag` | `TBD` | Quarterly |

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
