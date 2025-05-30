# ETL Pipeline Documentation

1. [Database](#database)
    1. [Schemas](#schemas)
2. [Scrapers](#scrapers)
    1. [Data Sources](#data-source-url)
    2. [Structure](#structure)

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

There is one scraper that needs to be ran hourly, [*Insert Number*] scrapers that requires to be run daily, and 4 that needs to be ran quarterly. They are structured using abstract classes. The `EtlPipeline` class is the parent class of all scrapers. This class has two direct children: `StationObservationPipeline`, and `DataBcPipeline`. The former has observed hydrological and climate data sources, and requires the `station_ids` that the database has to associate the data to the correct station. On the other hand, the `DataBcPipeline` scraper water licensing data for BC. The general structure of the classes are below:

![BCWAT UML Diagram](/airflow/etl_pipelines/readme_sources/BCWAT_final_UML_diagram.png)

As mentioned, the above is the general structure followed by most of the scrapers. There are cases that the individual scrapers overwrites the parents function due to specific needs of the scrapers.

Each scraper is separated into their respective AirFlow DAG, keeping the workflow separate and independent of other workflows.

This document will be updated with more information, such as the schedule that the DAGs run at, as well information on specific scrapers if they need any special attention once in a while. This document will be updated as the project progresses.
