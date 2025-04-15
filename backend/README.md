# Backend Documentation

## Contents

1. [AirFlow](#airflow)
2. [Database](#database)
    1. [Schemas](#schemas)  
3. [Scrapers](#scrapers)
    1. [Data Sources](#data-source-url)
    2. [Structure](#structure)
4. [API](#api)
    1. [Local Deploy](#running-the-api-locally)
    2. [Manual](#manual)
    3. [Start-Up Script](#start-up-script)
    4. [Dockerized](#dockerized)
5. [Unit Tests](#unit-tests)
    1. [Running the Tests](#running-the-tests)

## AirFlow

Apache AirFlow is the workflow orchestrator used to schedule the scraper jobs, as well as monitor for failures and initiate retries if possible. DAGs have been created and scheduled for each data file that requires scraping. 

[**ADD MORE**]

For more information on AirFlow see their [documentation](https://airflow.apache.org/docs/)

## Database

Distributed PostgreSQL database using CrunchyData.

[Add more info when DB is solidified]

### Schemas

#### `bcwat_obs`

Contains observation station metadata. Along with that, it will store the daily data for climate (temperature, precipitation, snow depth, snow water equivalence, and manual snow pillow), and water (discharge, level, and quality) based data.

#### `bcwat_lic`

Contains the water licensing data collected from DataBC geo-data that is available via WFS/WCS.

#### `bcwat_ws`

Contains watershed data that is required for the tool to create the watershed based analysis.

## Scrapers

### Data Source URL

Below is a list of URLs that the data files are collected from. Note that multiple data files are scraped from each URL.

List of Hourly/Daily URLs:

| Provider Name                         | URL                                                       |
|---------------------------------------|-----------------------------------------------------------|
|ECCC Data Catalogue                    |https://data-donnees.az.ec.gc.ca/data?lang=en              |
|BC Environment Data Search             |https://www.env.gov.bc.ca/wsd/data_searches/               |
|Drive BC                               |http://www.drivebc.ca/api/weather/observations?format=json |
|MSC Datamart                           |https://dd.meteo.gc.ca/                                    |
|VIU Hydromet                           |http://viu-hydromet-wx.ca                                  |
|BC Peace Weather                       |http://bcpeaceweather.com                                  |
|Pacific Climate Impacts Consortium     |https://www.pacificclimate.org/                            |
|FlowWorks                              |https://developers.flowworks.com/fwapi/v2/sites/|

**NOTE:** The FlowWorks API requires a bearer token to access their data.

List of Quarterly URLs:

| Provider Name                         | URL                                                       |
|---------------------------------------|-----------------------------------------------------------|
|BC Environment Data Search             |https://www.env.gov.bc.ca/wsd/data_searches/               |
|National Water Data Archive: HYDAT     |https://www.canada.ca/en/environment-climate-change/services/water-overview/quantity/monitoring/survey/data-products-services/national-archive-hydat.html |

In addition, DataBC geo data will be collected using Simon Norris's bcdata Python and CLI tool. For more information about this tool see the [bcdata repo](https://github.com/smnorris/bcdata).

### Structure

There are [*Insert Number*] data files that requires scraping. Of these data sources, one requires hourly scraping, [*Insert Number - 5*] requires daily scraping, and 4 requires quarterly scraping.

Each data source is separated into their respective AirFlow DAG, keeping the workflow separate and independent of other workflows.

Most scrapers either: need a station list to fetch the observations, or get data from DataBC. To accomodate these options, the pipeline will use an object oriented structure, with `ETLPipeline` abstract class as the base class. This class will be extended by either `StationObservationPipeline` abstract class if the data source requires the station list, or the `DataBCPipeline` abstract class if the data source is located on DataBC. To specialize the scrapers further, these two sub-classes will be extended through `<NightlyDataSourceName>Pipeline` class, where `<NightlyDataSourceName>` is an unique name of the data source that the class is for. 

## API

The backend is a RESTful API built using [Flask](https://flask.palletsprojects.com/), a lightweight Python web framework.

### Running the API Locally

The following commands assume you are within the `backend` directory. __It is dockerized using Python3.12. Ensure your local python version is the same.__

### Manual

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m gunicorn -w 4 wsgi:app
```

### Start Up Script

The `startup.sh` script performs the creation of a virtual environment, and installs all packages required for the API to run.

```bash
#!/bin/bash
chmod +777 ./startup.sh
./startup.sh
```

### Dockerized

```bash
docker build -t bcwat-api:local .
docker run -p 8000:8000 bcwat-api:local
```

## Unit Tests

[PyTest](https://docs.pytest.org/en/stable/contents.html) is used for unit testing of the API. Please adhere to this documentation for creating unit tests for utility functions and API routes.

### Running the tests

The `run_unit_tests.sh` script performs the creation of a virtual environment, and installs all packages required for the API to run.

```bash
chmod +777 ./run_unit_tests.sh
./run_unit_tests.sh
```

The above command runs all of the unit tests.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

The above command runs all of the unit tests.

To run specific tests, use the following command for;

- running all tests within test file

```bash
pytest tests/test_hello_world.py
```

- running specific test in file

```bash
pytest tests/test_hello_world.py::test_hello_world
```
