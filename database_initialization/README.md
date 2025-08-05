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

![bcwat_obs_erd_diagram](/database_initialization/readme_sources/bcwat_obs_erd_diagram.png)

#### `bcwat_lic` ERD Diagram

![bcwat_lic_erd_diagram](/database_initialization/readme_sources/bcwat_licence_erd_diagram.png)

#### `bcwat_ws` ERD Diagram

![bcwat_ws_erd_diagram](/database_initialization/readme_sources/bcwat_watershed_erd_diagram.png)

**NOTE:** All `latitude` and `longitude` values can be assumed to be in SRID 4326 unless stated otherwise.

## What it Does

If there is a database that needs to be populated, or repopulated with the base data, this is the script to run.

The function of this script is as follows:
1. Drop all schemas and it's contents
2. Recreate the schema with it's tables, constraints, and indices.
3. Populate the static data that will not change through scraping, as well as data that changes infrequently.
4. Populate the data that changes frequently, such as the observations and the license data.
5. Run the post import queries, such as triggers, and some manual inserts for new tables.

**NOTE**: This script does not create a new database if the database does not exist. So creating the database needs to be done manually before running this script.

## Info on Files

#### transfer_table.py

This file is the main file that handles all the arguments that get's passed in to determine which part of the script needs to be ran. The available flags are:
```
--recreate_db
    Use this to drop all schemas in the database and recreate schemas from scratch
--import_data
    Use this to truncate all tables and repopulate them with the static data as well as the scraped data. This should only be used if you are doing a data transfer from DB to DB
--aws_upload
    Use this flag to export the source data from the DB and convert it to CSV, which gets compressed using gzip, then uploaded to the S3 bucket that is specified in the .env file.
--aws_import
    Use this flag to download the compressed data from the S3 bucket, uncompress, and populate the destination database. This was made because the database on Openshift cannot be accessed from the outside.
--aws_cleanup
    Use this flag to delete all the data in the S3 bucket.
--aws_contents
    Use this flag to get the contents of the S3 bucket and print it to the console.
```

#### all_data_transfer.py

This is the main file that dictates the import of the data from the various files in the `queries` directory.

- `import_data` function is the function that gets called from the `transfer_table.py` file. This calls the `populate_all_tables` and the `run_post_import_queries`. It is basically the access point to these function from other files.

- `populate_all_tables` function takes in the destination database's connection and the dictionary to insert. The dictionary is defined in the `constants.py` file. Before insertion, specific tables get minor adjustments to the data. This is done here because of some of the changes that are required are a bit complicated to do in SQL, but very simple to do in Python. After the query is ran, 100000 rows of data is transferred at a time, if the schema is `bcwat_ws` then it is 2500 at a time because geometries are very heavy. Some JSON columns are transformed in to JSON objects, this has to be done because psycopg2 returns JSON columns as string columns.

- `run_post_import_queries` runs the queries in the `post_import_queries.py` file, which consists mostly of triggers, indices, and some manual changes to the data that needs to be made afterwards.

- `create_csv_file` function is used when the `--aws_upload` flag is active. This will export the data that is needed to populate the databse to a CSV file. The CSV file is then sent to the S3 bucket specified in the `.env` file. The CSV file is deleted after upload

- `import_from_s3` is the opposite function to `create_csv_file`. When the `--aws_import` flag is used, the CSV files are opened within the S3 bucket, then imported into the destination database. The amount of data that is read is controlled by the `chunk_size` variable, and the reading of that chunk from S3 is done by the `open_file_in_s3` function. The file is read in chunks until the `chunk_start` value is larger than the `file_size` value.

- `insert_missing_stations` will insert new stations that are not in the database when the import data flag is used. The new station data is stored in the [`new_stations.csv`](new_stations.csv) file. The CSV file only consists of new stations from scrapers that does not have the function to automatically add new stations. , `construct_insert_tables`, and `insert_new_stations` are taken directly from the [`StationObservationPipeline`](../airflow/etl_pipelines/scrapers/StationObservationPipeline/StationObservationPipeline.py) class.

#### util.py

The file consists of utility functions that are used multiple times in other files. These functions mostly consists of getting connection to the various databases specified in the `.env` file.

- `get_from_conn`, `get_wet_conn`, and `get_to_conn` are functions used to get the database connection to three different databases, specified using the `.env` file.

- `recreate_db_schema` is used to basically start a clean version of the database.

- `special_variable_function` is a function used for the `bcwat_obs.variable` table to do some minor adjustments to the data. This is needed because originally the variables were split into two separate tables. The `polars` boolean that it accepts allows it to switch from a Panadas transformation to a Polars transformation.

- `create_partitions` creates partitions on two tables: `bcwat_obs.station_observation` and `bcwat_obs.water_quality_hourly` so that querying to them is faster.

- `delete_partitions` deletes the partitions that were created by the above function.

- `send_file_to_s3` will authenticate to the specified S3 bucket, using the credentials provided in the `.env` file. Once authenticated, the CSV will be uploaded in to the bucket.

- `determine_file_size_s3` will take an argument `file_name` which is the Key to the contents of the S3 Bucket. It will find the size of the file in bytes, and return it. This value is used to determine when the file import is finished.

- `open_file_in_s3` will open the CSV file that is specified by the `file_name` argument, without downloading. The data is read in chunks that are specified by the `chunk_start` and `chunk_end` arguments. The binary string is returned, along with the next `chunk_start` and `chunk_end` values.

- `check_temp_dir_exists` will create the `temp` directory if it does not exist. This is where the CSV files will be writtend to before sending them to S3.

- `clean_aws_s3_bucket` is a function used to delete all the files that exists in the S3 Bucket specified in the `.env` file.

- `make_table_from_to_db` is a function that will run a specific SQL query to populate the `station_region` table in the `bcwat_obs` schema. This is a special function because this is the only table that can be populated strictly with data that already exists in the `bcwat_obs` schema.

- `get_contents_of_bucket` is a function that will print out the contents of the S3 bucket specified in the `.env` file.

- `construct_insert_table` is a function that creates the new stations list and the metadata that needs to be inserted in to the database using the `new_stations.csv` file. The function is taken directly from the [`StationObservationPipeline`](../airflow/etl_pipelines/scrapers/StationObservationPipeline/StationObservationPipeline.py) class.

- `insert_new_stations` will insert the new stations and it's metadata into the database. This function is taken directly from the [`StationObservationPipeline`](../airflow/etl_pipelines/scrapers/StationObservationPipeline/StationObservationPipeline.py) class.

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

- `nwp_stations`: A dictionary with the origin table as keys, and values being a list with the following:
    ```
    [<destination_table_name>, <query>, <destination_schema>, <needs_station_id_join>]
    ```
    This dict consists of the data that needs to be joined to the `nwp_flow_metric` data, as well as the `extreme_flow` data.

- `climate_var_id_conversion`: A dictionary with the original `variable_id` as keys and the new `variable_id`s as values. This is required because in the original database, the climate variables and water variables are not in the same table.

- `data_import_dict_s3`: This is a dictionary that is used to dictate the order that the files should be downloaded/imported from the S3 bucket, as well as the transformations required for before it goes into the database. The values of the keys are also a dictionary with the following structure:
    ```
    key: {"tablename": string, "schema": string, "needs_join": Boolean, "dtype": dictionary}
    ```
    Where the `"tablename"` is the name of the destination table, `"schema"` is the name of the destination schema, `"needs_join"` indicates whether the data needs to be joined to a separate table or not, and `"dtype"` is a dictionary with column names and Polars data types that the CSV files should be read as.

- `geom_column_names4326` and `geom_column_names3005` are columns that needs to be transformed in to geometry columns using `polars_st`. They are separated in to two lists because they require different coordinate systems, 4326, and 3005, respectively.

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

At the bottom of the file, there is a view that is created in the database. This view is the aggregation of the following tables:

- `bcwat_lic.bc_wls_wrl_wra`
- `bcwat_lic.bc_wls_water_approval`
- `bcwat_lic.licence_ogc_short_term_approval`

These are turned into a view since they all go to the same location in the frontend, and it is easier for the API to look at instead of having to do all the joins and manipulation there.

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
    ems_archive_update.py
    hydat_import.py
    moe_hydrometric_historic.py
    water_quality_eccc.py
```

Similar to the `bcwat_lic` schema, there is a view being created at the end of the file. This is just to easily identify the stations that should be scraped. This separated by networks, allowing us to easily query for the correct stations to scrape.

#### queries/bcwat_watershed_erd_diagram.py

This file consists of all the table and relations required to reproduce the `bcwat_ws` schema.

The schema will hold static, and non-static data for the watershed analysis that the BCWAT tool does. There is no scraper that will insert into this schema.

#### queries/post_import_queries.py

This file contains all the queries that need to be run after the static data is imported. It is mostly triggers that need to be set on some tables, as well as some manual inserts, and indices creation. This needs to happen after the data import is completed, else either the trigger will apply the function on data that is already correct or will try to insert an extra row to some tables, or the manual insert will look for data that does not exist.

There are also some PostgreSQL functions that are required for the API to function. Documentation for these functions are below:

##### `bcwat_lic.get_allocs_per_wfi`
This function will get the water licences that are within the upstream watershed of the `in_wfi` provided for the functions. This is the base of all the function, meaning that this is the only SQL function that does not call the other functions.

##### `bcwat_lic.get_allocs_adjusted_quantity`
This function calls the first function to gather the water licences in the upstream watershed of the provided `in_wfi`. The `in_basin` value can be changed to get the water licences associated with the downstream watershed of the upstream watershed. Minor adjustments are made to the data.

##### `bcwat_lic.get_allocs_adjusted_quantity`
Returns the water allocations in m3 for a list of industries. Each industries' allocation is split in to 4 categories: `surface water long term`, `surface water short term`, `ground water long term`, and `ground water long term`. This data is used to represent the allocations for each industry for the queried watershed, and will be shown as a horizontal bar graph in the report. This function calls the first function to gather it's data.

##### `bcwat_lic.get_each_allocs_monthly`
Calls the `bcwat_lic.get_allocs_adjusted_quantity` function to gather the data required for transformation. Each licence's allocation is separated in to monthly values, with some alterations done depending on the licence purpose. For example, `irrigation`, and `lawn, fairway, and garden care` are calculated in the same way, but the allocations for `mining`, and `transportation management` are calculated in a slightly different way. All storage values are ignored in this calculation case.

##### `bcwat_lic.get_allocs_monthly`
Calls the function `bcwat_lic.get_each_allocs_monthly` to get the data required. This function simply summs the monthly values in to groups. The total allocation is also calculated.

##### `bcwat_lic.get_monthly_hydrology`
Calls the function `bcwat_lic.get_allocs_monthly` with the queried watershed's `region_id` value. This function is mostly used to aggregate the data required for the report.

The parameters for these functions are all a subset of the following list of variables:

| Parameter Name | Type | Description |
| --- | --- | --- |
| `in_wfi` | `Integer` | The watershed feature ID of the watershed of interest. |
| `in_basin` | `String` | Usually the values are `query` or `downstream`, and is passed in with the `in_wfi` parameter. `query` indicates that the watershed of interest is the `in_wfi` watershed, and `downstream` indicates that the downstream watershed of `in_wfi` is the watershed of interest. |
| `in_table_name` | `String` | The table that the function should use to gather it's data. It will default to the `bcwat_lic.licence_wls_map` value, which is used almost all of the time. |
| `in_region_id` | `Integer` | Never has to be specified, this is automatically calculated by the functions. If you ever need to specify the `in_region_id` value, then please refer to the table below. |
| `in_datestamp` | `String` | Date that the data should be fetched from. Defaults to the current date in UTC. |

##### Region Table:
| Region Name | Region ID |
| --- | --- |
| Cariboo | 3 |
| Kootney | 4 |
| Omineca | 5 |
| Skeena Region + Section of Northeast Region + Haida Guaii | 6 |

###### NOTE The watershed reports does not cover the all or majority of the following regions:
- Northeast Region
- West Coast Region
- South Coast Region
- Thompson - Okanagan Region


#### queries/bcwat_obs_data.py

This file contains all the queries that needs to be ran to collect all the necessary data to complete a data migration from the original db to the new db. There are some queries that needs the `old_station_id`s of the stations that got inserted in to the `station` table. Those queries MUST be AFTER the `stations` entry in the dictionary, or else those queries that require the new `station_ids` will fail.

#### queries/bcwat_licence_data.py

This file contains all the queries that needs to be ran to collect all the necessary data to complete a data migration from the original db to the new db for the `bcwat_lic` schema.

#### queries/bcwat_watershed_data.py

This file contains all the queries that needs to be ran to collect all the necessary data to complete a data migration from the original db to the new db for the `bcwat_ws` schema.

The majority of the data in this database does not receive updates or transformations. So instead of keeping them as tables with `n` columns, they have been reshaped in to a table with a primary key column(s), and a JSON column where the JSON consists of all the data that used to be individual columns.

## How to Run

To run this script do the following:

1. create and populate `.env` file in the `database_initialization` directory using the `.env.example`. The `from` database should be either `bcwt-dev` on Moose or `ogc` on Aqua-DB2. The `to` database should be the database you are trying to populate, and the `wet` should be `bcwt-staging` on Moose. If exporting or importing to an S3 bucket, the AWS related variables must be filled as well.

2. Create a Python venv, and activate it with the following:

    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3. Run the script with the following:
    ```
    python transfer_table.py --aws_cleanup --aws_upload --aws_import
    ```
    And that should run the script.

    This will delete all files from the specified S3 Bucket, export the data to the S3 Bucket in CSV form, and then import the data from the S3 Bucket into the destination database.

For any question or issues, please contact Kashike Umemura @ kumemura@foundryspatial.com (for now)
