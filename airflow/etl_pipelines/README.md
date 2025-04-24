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

There are [*Insert Number*] data files that requires scraping. Of these data sources, one requires hourly scraping, [*Insert Number - 5*] requires daily scraping, and 4 requires quarterly scraping.

Each data source is separated into their respective AirFlow DAG, keeping the workflow separate and independent of other workflows.

Most scrapers either: need a station list to fetch the observations, or get data from DataBC. To accomodate these options, the pipeline will use an object oriented structure, with `ETLPipeline` abstract class as the base class. This class will be extended by either `StationObservationPipeline` abstract class if the data source requires the station list, or the `DataBCPipeline` abstract class if the data source is located on DataBC. To specialize the scrapers further, these two sub-classes will be extended through `<NightlyDataSourceName>Pipeline` class, where `<NightlyDataSourceName>` is an unique name of the data source that the class is for. 
