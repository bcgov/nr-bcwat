# ETL Pipeline Documentation

1. [Database](#database)
    1. [Schemas](#schemas)
2. [Scrapers](#scrapers)
    1. [Data Sources](#data-source-url)
    2. [Structure](#structure)
    3. [Special Cases](#special-cases)
        1. [drive_bc.py](#drive_bcpy)

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

The following table has the scraper file name, the source that it is scraping from, the description of the data that it is scraping, and the variables that it is scraping.

| Scraper Name | Source | Description | Variables |
| --- | --- | --- | --- |
| [`asp.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/climate/asp.py) | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/) | Automated Snow Pillow (ASP) data from automated stations.| <ul><li>Temperature</li><li>Precipitation</li><li>Snow Depth</li><li>Snow Water Equivalent (SWE)</li></ul> |
| [`drive_bc.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/climate/drive_bc.py) | [Drive BC](http://www.drivebc.ca/) | The only scraper that runs hourly. Collects data from the DriveBC API. The hourly data is converted in to daily data once a day. | <ul><li>Snow Depth</li><li>Temperature</li><li>Precipitation Amount</li><li>Hourly Precipitation</li></ul>
| [`ec_xml.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/climate/ec_xml.py) | [MSC Data Mart](https://dd.meteo.gc.ca/) | MSC Data Mart XML Scraper. | <ul><li>Temperature</li><li>Precipitation</li><li>Wind</li><li>Snow Amount</li></ul> |
| [`env_aqn`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/climate/env_aqn.py) | [BC Ministry of Environment](https://www.env.gov.bc.ca/epd/bcairquality/aqo/csv/Hourly_Raw_Air_Data/Meteorological/) | Data from the Ministry of Environment. This data originally came from PCIC. | <ul><li>Temperature</li><li>Precipitation</li></ul> |
| [`env_hydro.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/water/env_hydro.py) | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/water/) | Water stage and discharge from BC Government. | <ul><li>Discharge</li><li>Level</li></ul> |
| [`flnro_wmb.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/climate/flnro_wmb.py) | [BC Ministry of Forest](https://www.for.gov.bc.ca/ftp/HPR/external/!publish/BCWS_DATA_MART/) | FLNRO-WMB data from the Ministry of Forest. Was originally from PCIC data porta. | <ul><li>Temperature</li><li>Precipitation</li></ul> |
| [`flow_works.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/water/flow_works.py) | Data from FlowWorks API | The access to the FlowWorks API requires an bearer token. | <ul><li>Temperature</li><li>Precipitation</li><li>Dischage</li><li>Level</li><li>Snow Water Equivalent</li><li>Rainfall</li></ul> |
| [`gw_moe.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/water/gw_moe.py) | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/) | Groundwater data from the Ministry of Environment. | <ul><li>Groundwater Level</li></ul> |
| [`msp.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/climate/msp.py) | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/) | Manual Snow Pillow data from the Ministry of Environment. | <ul><li>Snow Depth</li><li>Snow Water Equivalent</li><li>Percent Density</li></ul> |
| [`water_licences_bcer.py`](/airflow/etl_pipelines/scrapers/DataBcPipeline/licences/water_licences_bcer.py) | BC-ER ArcGIS Layer | Data from an ArcGIS data layer | <ul><li>Short Term Approvals</li></ul> |
| [`weather_farm_prd.py`](/airflow/etl_pipelines/scrapers/StationObservationPipeline/climate/weather_farm_prd.py) | [BC Peace River Regional District Data](http://www.bcpeaceweather.com/api/WeatherStation/) | Data From BC Peace River Regional District weather stations. Some of the stations are not returning data but some of them work. | <ul><li>Temperature</li><li>Rainfall</li></ul> |
| [`water_approval_points.py`](/airflow/etl_pipelines/scrapers/DataBcPipeline/licences/water_approval_points.py) | [DataBC Data Catalogue](https://catalogue.data.gov.bc.ca/) | Data from DataBC scraped using the [`bcdata`](https://github.com/smnorris/bcdata) Python package. This scraper scrapes the Water Rights Approval Points | <ul><li>Water Rights Approval Points</li></ul> |
| [`water_rights_applications_public.py`](/airflow/etl_pipelines/scrapers/DataBcPipeline/licences/water_rights_applications_public.py) | [DataBC Data Catalogue](https://catalogue.data.gov.bc.ca/) | Data from DataBC scraped using the [`bcdata`](https://github.com/smnorris/bcdata) Python package. This scraper scrapes the Public Water Rights Applications | <ul><li>Public Water Rights Applications</li></ul> |
| [`water_rights_licences_public.py`](/airflow/etl_pipelines/scrapers/DataBcPipeline/licences/water_rights_licences_public.py) | [DataBC Data Catalogue](https://catalogue.data.gov.bc.ca/) | Data from DataBC scraped using the [`bcdata`](https://github.com/smnorris/bcdata) Python package. This scraper scrapes the Public Water Rights Licences | <ul><li>Public Water Rights Licences</li></ul> |

**NOTE:** The FlowWorks API requires a bearer token to access their data.

List of Quarterly URLs:

| Scraper Name | Source | Description | Variables |
| --- | --- | --- | --- |
| [`climate_ec_update.py`](/airflow/etl_pipelines/scrapers/QuarterlyPipeline/quarterly/climate_ec_update.py) | [MSC Data Mart](https://dd.meteo.gc.ca/) | BC Climate daily data from MSC Data Mart | <ul><li>Temperature</li><li>Precipitation</li><li>Snow Depth</li><li>Snow Amount</li></ul> |
| [`gw_moe.py`](/airflow/etl_pipelines/scrapers/QuarterlyPipeline/quarterly/gw_moe.py) | [BC Ministry of Environment](http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/) | Groundwater data from the Ministry of Environment. Similar source to the daily `gw_moe` scraper, but this takes the average .csv file. | <ul><li>Groundwater Level</li></ul> |
| [`hydat_import.py`](/airflow/etl_pipelines/scrapers/QuarterlyPipeline/quarterly/hydat_import.py) | [Hydat](https://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/) | Hydat database which comes in a `.zip` format. Must be decompressed to be accessed. | <ul><li>Water Discharge</li><li>Water Level</li></ul> |
| [`water_quality_eccc.py`](/airflow/etl_pipelines/scrapers/QuarterlyPipeline/quarterly/water_quality_eccc.py) | [ECCC Data Catalogue](https://data-donnees.az.ec.gc.ca/) | Water quality data from various locations. Gathered via the ECCC Data Catalogue API. | <ul><li>Water Quality</li></ul> |
| [`moe_hydrometric_historic.py`](/airflow/etl_pipelines/scrapers/QuarterlyPipeline/quarterly/moe_hydrometric_historic.py) | [ECCC Data Catalogue](https://data-donnees.az.ec.gc.ca/) | Discharge and Stage data from the Ministry of Environment | <ul><li>Discharge</li><li>Stage</li></ul> |

### Structure

There is one scraper that needs to be ran hourly, [*Insert Number*] scrapers that requires to be run daily, and 4 that needs to be ran quarterly. They are structured using abstract classes. The `EtlPipeline` class is the parent class of all scrapers. This class has two direct children: `StationObservationPipeline`, and `DataBcPipeline`. The former has observed hydrological and climate data sources, and requires the `station_ids` that the database has to associate the data to the correct station. On the other hand, the `DataBcPipeline` scraper water licensing data for BC. The general structure of the classes are below:

![BCWAT UML Diagram](/airflow/etl_pipelines/readme_sources/BCWAT_final_UML_diagram.png)

As mentioned, the above is the general structure followed by most of the scrapers. There are cases that the individual scrapers overwrites the parents function due to specific needs of the scrapers.

Each scraper, except for the `water_rights_applications_public.py`, and `water_rights_licences_public.py` scrapers, are separated into their respective AirFlow DAG, keeping the workflow separate and independent of other workflows. To see the reason for the exception for the two scarpers, see the [`README.md`](/airflow/README.md) file's `Notable DAGs` section.

### Special Cases

Some scrapers have special methods only available to themselves to deal with their different data formats. This section will explain them in more detail.

#### `drive_bc.py`

Because the data that we collect from DriveBC is hourly observation with no historical archives that we can collect data from, it is necessary to scrape the hourly data. Since the frontend only shows daily data, this hourly data must be converted in to daily data. The `drive_bc.py` scraper has two special methods to complete this conversion:
|Function Name|Arg Name: Type|
|---|---|
|`convert_houly_data_to_daily_data`|N/A|
|`__create_daily_data_dataframe`| <ul><li>`data` : polars.LazyFrame</li><li>`metadata`: dictionary</li></ul>|

The first method is called from a DAG that is separate from the DAG that scrapes the data ([`drive_bc_dag.py`](/airflow/dags/drive_bc_dag.py)). It is the main access point to the time conversion functionality, and calls the second method for the actualy aggregation of the values. The constant dict `DRIVE_BC_HOURLY_TO_DAILY` exists to ensure that the correct windows are selected for aggregation.

The second method is called with daily data, and metadata for which variable to transform, using a specified time window, and aggregation method. Within the method, there is minial changes to the data other than the aggregation. Some variable's ID's are changed to reflect the correct variable after aggregation.

#### `gw_moe.py`

This class consists of the daily scraper code as well as the quarterly scraper code. This is because the data each time period injests is very similar to each other.

In the constructor of the class, the flag `quarterly` is set as a boolean value. When this is set to `True`, the class will run the quarterly scraper code. When it is set to `False`, the class will run the daily scraper code. The differences are very minor, so a whole separate class is not necessary.

#### `hydat_import.py`

This is the most resource hungry scraper of all the scrapers being ran. The file that is downloaded is a `.zip` file that uncompresses to be a `Hydat.sqlite3` database file. All data from stations within BC must be extracted, transformed, and loaded to the database.

The fact that this file comes in a `.zip` file requires complete overwrites of the download, and transform methods. Furthermore, methods that check for stations, as well as extraction methods have been written to accompany this scraper.
