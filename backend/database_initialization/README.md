# Database and Database Initialization Directory Documentation

## Table of Contents:
1. [Purpose of This Directory](#purpose-of-this-directory)
2. [What it does](#what-it-does)
3. [Structure of the Database](#structure-of-the-database)
    1. [bcwat_obs ERD Diagram](#bcwat_obs-erd-diagram)
    2. [bcwat_lic ERD Diagram](#bcwat_lic-erd-diagram)
    3. [bcwat_ws ERD Diagram](#bcwat_ws-erd-diagram)
4. [Info on Files](#info-on-files)
    1. [transfer_table.py](#transfer_tablepy)
    2. [all_data_transfer.py](#all_data_transferpy)
    3. [util.py](#utilpy)
    4. [constants.py](#constantspy)
    5. [queries/bcwat_license_erd_diagram.py](#queriesbcwat_license_erd_diagrampy)
    6. [queries/bcwat_obs_erd_diagram.py](#queriesbcwat_obs_erd_diagrampy)
    7. [queries/bcwat_watershed_erd_diagram.py](#queriesbcwat_watershed_erd_diagrampy)
    8. [queries/post_import_queries.py](#queriespost_import_queriespy)
    9. [queries/bcwat_obs_data.py](#queriesbcwat_obs_datapy)
    10. [queries/bcwat_licence_data.py](#queriesbcwat_licence_datapy)
    11. [queries/bcwat_watershed_data.py](#queriesbcwat_watershed_datapy)
5. [How to Run](#how-to-run)

## Purpose of This Directory
This directory contains all the code that is neccessary to initialize the database. Once this script is ran, the database will be populated with the correct static data in the correct format and location.

This script was made so that the process of recreating the database from scratch is very easy to do.

## Structure of the Database

Each of the schemas in the database has been made so that there is little to no interdependencies between them. Following are the Entity Relation Diagrams of each schema in the database.

#### `bcwat_obs` ERD Diagram

![bcwat_obs_erd_diagram](/backend/database_initialization/readme_sources/bcwat_obs_erd_diagram.png)

#### `bcwat_lic` ERD Diagram

![bcwat_lic_erd_diagram](/backend/database_initialization/readme_sources/bcwat_licence_erd_diagram.png)

#### `bcwat_ws` ERD Diagram

![bcwat_ws_erd_diagram](/backend/database_initialization/readme_sources/bcwat_watershed_erd_diagram.png)

**NOTE:** All `latitude` and `longitude` values can be assumed to be in SRID 4326 unless stated otherwise.

## What it Does

If there is a database that needs to be populated, or repopulated with the base data, this is the script to run.

The function of this script is as follows:
1. Drop all schemas and it's contents
2. Recreate the schema with it's tables, constraints, and indices.
3. Populate the static data that will not change through scraping, as well as data that changes infrequently.
4. Populate the data that changes frequently, such as the observations and the license data. **Not implemented yet**
5. Run the post import queries, such as triggers, and some manual inserts for new tables.

**NOTE**: This script does not create a new database if the database does not exist. So creating the database needs to be done manually before running this script.

## Info on Files

#### transfer_table.py

This file is the main file that handles all the arguments that get's passed in to determine which part of the script needs to be ran. The available flags are:
```
--recreate_db
    Use this to drop all schemas in the database and recreate schemas from scratch
--non_scraped
    Use this to truncate all tables and repopulate them
```

#### all_data_transfer.py

This is the main file that dictates the import of the data from the various files in the `queries` directory.

The `import_data` function is the function that gets called from the `transfer_table.py` file. This calls the `populate_all_tables` and the `run_post_import_queries`. It is basically the access point to these function from other files.

The `populate_all_tables` function takes in the destination database's connection and the dictionary to insert. The dictionary is defined in the `constants.py` file. Before insertion, specific tables get minor adjustments to the data. This is done here because of some of the changes that are required are a bit complicated to do in SQL, but very simple to do in Python.After the query is ran, 1 000 000 rows of data is transferred at a time. Some JSON columns are transformed in to JSON objects, this has to be done because psycopg2 returns JSON columns as string columns.
The `run_post_import_queries` runs the queries in the `post_import_queries.py` file.

#### util.py

The file consists of utility functions that are used multiple times in other files. These functions mostly consists of getting connection to the various databases specified in the `.env` file. There are a few other functions, like setting up logging, and small processing of data for specific tables. The function that recreates the schemas in the database also exists in this file.

#### constants.py

This file contains the constants used in the database initialization process. It contains the following dictionaries:
- `bcwat_obs_data`: A dictionary with the origin table as keys, and values being a list with the following:
    ```
    [<destination_table_name>, <query>, <destination_schema>, <needs_station_id_join>]
    ```
    This dict consists of the data that needs to be imported in to the `bcwat_obs` schema.

- `bcwat_licence_data`: A dictionary with the origin table as keys, and values being a list with the following:
    ```
    [<destination_table_name>, <query>, <destination_schema>, <needs_station_id_join>]
    ```
    This dict consists of the data that needs to be imported in to the `bcwat_lic` schema.

- `bcwat_watershed_data`: A dictionary with the origin table as keys, and values being a list with the following:
    ```
    [<destination_table_name>, <query>, <destination_schema>, <needs_station_id_join>]
    ```
    This dict consists of the data that needs to be imported in to the `bcwat_ws` schema.

- `climate_var_id_conversion`: A dictionary with the original `variable_id` as keys and the new `variable_id`s as values. This is required because in the original database, the climate variables and water variables are not in the same table.

The constants are used to create the database schema and populate the tables with data from the source database.

#### queries/bcwat_license_erd_diagram.py

This file consists of all the table and relations required to reproduce the `bcwat_lic` schema.

The schema will hold the static data required for DataBC water-licensing data, as well as the data scraped from the DataBC scrapers. The following are the DataBC scrapers that will insert in to this schema:
```
/airflow/etl_pipelines/scrapers/DataBcPipeline/licences/
    water_approval_points.py
    water_licences_bcer.py
    water_rights_applications_public.py
    water_rights_licences_public.py
```

#### queries/bcwat_obs_erd_diagram.py

This file consists of all the table and relations required to reproduce the `bcwat_obs` schema.

The schema will hold the static data required for station based water (discharge, stage), and climate (temperature, precipitation, etc.) data from various data sources. Following are the scrapers that will insert in to this schema:
```
/airflow/etl_pipelines/scrapers/StationObservationPipeline/
    ./water/
        env_hydro.py
        flow_works.py
        gw_moe.py
        wsc_hydrometric.py
    ./cliamte/
        env_aqn.py
        asp.py
        drive_bc.py
        ec_xml.py
        flnro.py
        msp.py
        viu_fern.py
        weather_farm_prd.py

/airflow/etl_pipelines/scrapers/QuarterlyPipeline/quarterly/
    climate_ec_update.py
    gw_moe_quarterly.py
    hydat_import.py
    water_quality_eccc.py
```

#### queries/bcwat_watershed_erd_diagram.py

This file consists of all the table and relations required to reproduce the `bcwat_ws` schema.

The schema will hold static, and non-static data for the watershed analysis that the BCWAT tool does. There is no scraper that will insert into this schema.

#### queries/post_import_queries.py

This file contains all the queries that need to be run after the static data is imported. It is mostly triggers that need to be set on some tables, as well as some manual inserts. This needs to happen after the data import is completed, else either the trigger will apply the function on data that is already correct or will try to insert an extra row to some tables, or the manual insert will look for data that does not exist.

#### queries/bcwat_obs_data.py

This file contains all the queries that needs to be ran to collect all the necessary data to complete a data migration from the original db to the new db. There are some queries that needs the `station_ids` of the stations that got inserted in to the `station` table. Those queries MUST be AFTER the `stations` entry in the dictionary, or else those queries that require the new `station_ids` will fail.

#### queries/bcwat_licence_data.py

This file contains all the queries that needs to be ran to collect all the necessary data to complete a data migration from the original db to the new db for the `bcwat_lic` schema.

#### queries/bcwat_watershed_data.py

This file contains all the queries that needs to be ran to collect all the necessary data to complete a data migration from the original db to the new db for the `bcwat_lic` schema.

## How to Run

To run this script do the following:

1. create and populate `.env` file in the `database_initialization` directory using the `.env.example`. The `from` database should be either `bcwt-dev` on Moose or `ogc` on Aqua-DB2. The `to` database should be the database you are trying to populate, and the `wet` should be `bcwt-staging` on Moose.

2. Create a Python venv, and activate it with the following:

    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Run the script with the following:
    ```
    python transfer_table.py --recreate_db --non_scraped
    ```
    And that should run the script.

    If you don't want to include one of the options, then the default is false. So removing the arg will make sure that it will not run the script.

For any question or issues, please contact Kashike Umemura @ kumemura@foundryspatial.com (for now)
