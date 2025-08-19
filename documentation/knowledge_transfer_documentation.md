# Knowledge Transfer Documentation
This is the documentation for Artifact #9 of the `Deliverable Documentation`

## Contents:
1. [How changes are made to the model](#how-changes-are-made-to-the-model)
    1. [Database Changes](#database-changes)
    2. [Airflow Scraper Changes](#airflow-scraper-changes)
        1. [Addition of New Data Sources](#addition-of-new-data-sources)
2. [Triggers for model updates](#triggers-for-model-updates)
3. [Implmentation process for updates or code fixes](#implmentation-process-for-updates-or-code-fixes)
4. [Historical and current issues relating to BC Water Tools and their resolution](#historical-and-current-issues-relating-to-bc-water-tools-and-their-resolution)
5. [Data connections, sources, and agreements with third parties](#data-connections-sources-and-agreements-with-third-parties)
6. [Data refresh/update processes](#data-refreshupdate-processes)
7. [Procedures for handling broken connections and associated fixes.](#procedures-for-handling-broken-connections-and-associated-fixes)
8. [Process for adding a new region to the framework (explicitly included)](#process-for-adding-a-new-region-to-the-framework-explicitly-included)
    1. [Produce hydrology model](#produce-hydrology-model)
        1. [Annual Water Balance](#annual-water-balance)
        2. [Monthly Runoff](#monthly-runoff)
    2. [Translate monthly mean discharge from hydrology model into fundamental units from Freshwater Atlas](#translate-monthly-mean-discharge-from-hydrology-model-into-fundamental-units-from-freshwater-atlas)
    3. [Calculate upstream watershed polygons, and lookup tables for every fundamental watershed in the new region](#calculate-upstream-watershed-polygons-and-lookup-tables-for-every-fundamental-watershed-in-the-new-region)
    4. [Clean to remove holes and multi-part features](#clean-to-remove-holes-and-multi-part-features)
    5. [Calculate fundamental watershed attributes for other components for the reports](#calculate-fundamental-watershed-attributes-for-other-components-for-the-reports)
        1. [Climate](#climate)
        2. [Topography](#topography)
        3. [Land Cover](#land-cover)

## How changes are made to the model

This section will be done in two parts, [Database Changes](#database-changes), and [Airflow Scraper Changes](#airflow-scraper-changes).
Updating the hydrological model for the Watershed module will be covered in the [Process for adding a new region to the framework](#process-for-adding-a-new-region-to-the-framework-explicitly-included) section

### Database Changes

Database changes will be done using FlyWay Migrations. The process is the following:

1. Create a branch of the repository, create a FlyWay migration SQL file in the `nr-bcwat/migrations/sql/` directory, and named in the following format
    ```
    vX.Y.Z__<description>.sql
    ```
    Where the `X`, and `Y` values are the same as the other files in the directory, and the `Z` value is incremented by `1` for each change. The `<description>` should be a very short description of the changes being made.

2. Stage, commit, and push the changes to the repository.

3. Upon creation of the PR, the FlyWay migration will apply and the development environment database will be updated with the changes.

> [!WARNING]
> Step 3 has major issues due to the fact that a fresh database cannot be created for each PR. Because of this the development database is shared between **ALL** PRs. The issues that it can cause include, but are not limited to the following:
> 1. The migration that has been applied cannot be rolled back without connecting to the database and undoing it manually. This is a major issue when the change is removing rows or columns from the database
> 2. If there are two PRs with FlyWay migrations, then it is possible for one of the migrations to succeed, but the other one to fail if they have the exact same file version. If they have different vesions, it is possible for them to be applied in the wrong order. And if the migrations chages the same tables, the result might be something that is not expected at all.
> 3. Creating a PR with FlyWay migration, then closing the PR and deleting the branch will cause the FlyWay migration to be applied, but closing the PR will not rollback the changes. This will cause the API deployment to be broken on dev due to the incorrect FlyWay migration history.
>
> There are a couple of ways to mitigate this issue from happening, but all of them limit the rate of development, but are highly recommended to prevent any major issues.
> - Create a local version of the database that every database change is tested on **BEFORE** making a PR. The backups can be accessed via the S3 bucket for this project
> - Only have at most one PR open with a database change in it.

4. Once the PR is approved, and merged in to the `main` branch, the test deployment of the database will have the FlyWay migrations applied to it.

5. To promote the changes to prod, a GitHub action which promotes the test image to be the prod image needs to be ran, and the FlyWay migrations will be applied to the production database.

> [!NOTE]
> For any major database changes, please refer to [Major Database Changes](#major-database-changes) section of the Implementation process for updates or code fixes section.

### Airflow Scraper Changes

Any adjustment to the scrapers will follow these steps:

1. Create a branch of the repository, make the changes to the scrapers in `nr-bcwat/airflow/etl_pipelines/scraper/` as required. To make changes to the scheduling or the functions that Airflow runs, look in the `nr-bcwat/airflow/dags/` directory.

2. Stage, commit, and push the changes to the repository

3. Make PR.

> [!NOTE]
> This will not spin up an instance of Airflow because it is rather resource intensive to have for each PR.

4. When the PR is merged into the `main` branch, the development **AND** test Airflow deployments will be updated with the latest changes.

5. To promote the changes to prod, a GitHub action needs to be ran to update the prod deplyment of Airflow.

#### Addition of New Data Sources

To add a new data source to the scrapers, the following must be done:

1. Create a FlyWay migration file with the metadata necessary for the scrapers to be implemented. Look at the current scraper implementations as well as the database tables in `bcwat_obs` schema to get an idea of what is required.

2. Populate the `nr-bcwat/airflow/etl_pipelines/utils/constants.py` file with the new data source and it's metadata. Look at the other values in there for an example.

3. Create a new scraper class in the proper directory, depending on the data source. After doing that, implement all the abstract methods that are required. Look at the other scraper implementations for an example.

4. Once you have implmented all the required methods, then test the scraper on a local instance of the database so that dev is not altered.

5. Once the scraper is functioning **CORRECTLY**, create an Airflow DAG for the scraper to run. There are already Airflow DAGs in the `nr-bcwat/airflow/dags/` directory. Use them as an example.

6. Update documentation and create unit tests for the scraper. After that it should be ready to be deployed to dev.

## Triggers for model updates

There are no triggers for models updates other then when the scrapers fail, or a bug is found in the data.

New data source additions are not required, and are only optional. Please ensure that any changes made are well documented incase they need to be reviewed by a third party in the future.

## Implmentation process for updates or code fixes

Code fixes and updates will be handled by GitHub and the flow that the BC Gov follows for most projects. But major database changes are done differently, and this will be outlined later in this section. The following are the steps for code changes to the ETL pipeline, backend, and frontend:

<ins>Step 1</ins>:\
Create a branch of the repository with the code changes made to the required section.

If this is a data model change, then make the change in a FlyWay migration SQL file in the `nr-bcwat/migrations/sql/` directory, and named in the following format
```
vX.Y.Z__<description>.sql
```
Where `X`, `Y`, and `Z` are the major, minor, and patch versions of the model, and the `<description>` should be a very short description of the changes being made. In most cases, incrementing the `Z` value by ` should suffice.

<ins>Step 2</ins>:\
After all change has been made, make sure that all tests pass for each of the `client`, `backend`, and `airflow` directories. How to run the tests is detailed in their respective `README.md` files:
- [client](/client/README.md)
- [backend](/backend/README.md)
- [airflow](/airflow/README.md)

If all tests pass, stage, commit, and push the changes to the repository. Once in the repository, the tests will be rerun by a GitHub Action. Ensure that this passes before moving on.

<ins>Step 3</ins>:\
Once all tests pass, create a PR for the changs and get someone to review them. When the PR is created, all changes to the flyway migration will be ran, the API and frontend will be spun up. Then you will be able to access the development environment application to ensure that the changes you made behave as expected.

<ins>Step 4</ins>:\
Once the PR is approved, and merged in, the test deployment of the application will be updated with the changes. Once all the tests pass, the prod environment will be updated.

#### Major Database Changes

Due to the nature of this project, any major database changes will be done in a different way. It will not use FlyWay migrations, and will likely require manual creations of jobs to run scripts to the database. Major database changes are defined as the following:
- Expansion of the `Watershed` Mdoule
- Addition of columns or rows that cannot be calculated from the existing Data

This is because for these changes, a large amount of data (>10Gb) must be imported to the database, and it will not be efficient to have that data in a FlyWay migration.

The generalized steps to complete the database changes are the following:

<ins>Step 1</ins>:\
Create a branch of the repository, and make a script that will import the data to the database from a S3 bucket. Make sure that you know whether you are replacing all the data, or only appending to the database.

In addition to the code, make sure that you have the following:
- `requirements.txt` file with all the dependencies for the script
- `Dockerfile` for the job that will be run.

<ins>Step 2</ins>:\
In the `.github/workflows/` directory, create a new workflow for the job that will be run. Look at the any of the `.yaml` files for an example on what it should look like. Make sure that the image is built on push.

Push the changes to the repository, and the Docker image should be built by the action.

<ins>Step 3</ins>:\
Ensure that your environment variables that are required for the job are in each namespace on the `Kamloops Silver Cluster` by checking each namespace. If they are not, then add them to each namespace.

<ins>Step 4</ins>:\
Make sure that the job will have access to the database by adding the necessary network policies to the namespace. Look at the examples in any of the directories in the `charts/` directory for an example on how to do this. They will be in the `knp.yaml` file.

Apply it to the name space by logging in to the openshift cluster, then running
```
oc apply -f knp.yaml
```

<ins>Step 5</ins>:\
Make the `.yaml` file to run the job with the proper secrets access. Look at the examples in any of the directories in the `charts/` directory for an example on how to do this. They will be the file that is not named `knp.yaml`.

Run the job by running the command
```
oc apply -f <name_of_job_file.yaml>
```

If you need to re-run the job, then you can delete the job from the namespace, make changes to your code, push, then apply Step 5 to run the job again.

## Historical and current issues relating to BC Water Tools and their resolution

## Data connections, sources, and agreements with third parties

Data shown in the BC Water Tools is obtained through publically available sources. The sources names and licence agreements are detailed in the following table

| Source | Licence URL |
| --- | --- |
| Water Survey of Canada |http://wateroffice.ec.gc.ca/disclaimer_info_e.html |
| Government of Newfoundland and Labrador | http://www.gov.nl.ca/disclaimer/index.html |
| Geoscience BC | http://www.geosciencebc.com/s/Home.asp |
| Surrey SCADA | http://data.surrey.ca/pages/open-government-licence-surrey |
| Delta | http://data.surrey.ca/pages/open-government-licence-surrey |
| BC Environmental Assessment Office (EAO) | https://www2.gov.bc.ca/gov/content/home/copyright |
| Oil and Gas Industry Network | N/A |
| BC MoE - Groundwater Observation Well Network | http://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/databc/open-data/open-government-license-bc |
| Department of Fisheries and Oceans | N/A |
| Agricultural and Rural Development Act Network | http://www.ec.gc.ca/default.asp?lang=En&n=12345678-1&xsl=mainhomeitem&xml=5830C36B-1773-4E3E-AF8C-B21F54633E0A |
| BC Hydro | http://www.bchydro.com/siteinfo/legal.html |
| BC FLNRORD - Forest Ecosystems Research Network | http://www2.gov.bc.ca/gov/admin/disclaimer.page |
| BC FLNRORD - Wild Fire Management Branch | https://www2.gov.bc.ca/gov/content/home/copyright |
| BC Ministry of Agriculture | https://www2.gov.bc.ca/gov/content/home/disclaimer |
| BC ENV - Air Quality Network | https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc |
| BC MoE - Automated Snow Pillow Network | http://www2.gov.bc.ca/gov/content/governments/about-the-bc-government/databc/open-data/open-government-license-bc |
| BC MoTI | http://www2.gov.bc.ca/gov/admin/copyright.page |
| Environment Canada | http://www.ec.gc.ca/default.asp?lang=En&n=12345678-1&xsl=mainhomeitem&xml=5830C36B-1773-4E3E-AF8C-B21F54633E0A |
| Forest Renewal British Columbia | N/A |
| RioTintoAlcan | http://www.riotintoalcan.com/site_terms_and_conditions.asp |
| BC ENV - Manual Snow Survey | https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc |
| Regulator – BC Oil and Gas Commission | http://www.bcogc.ca/terms-use |
| BC Peace Agri-WeatherNet | http://www.bcpeaceweather.com/ |
| Lake Windemere Ambassadors | N/A |
| Columbia Lake Stewardship Society | N/A |
| Friends of Kootenay Lake | info@friendsofkootenaylake.ca |
| Village of Belcarra | N/A |
| Wasa Lake Land Improvement District | nowellberg@gmail.com |
| Friends of Swan Creek | https://creativecommons.org/licenses/by-sa/3.0/ |
| ECCC - National Long-term Water Quality Monitoring Data | https://open.canada.ca/en/open-government-licence-canada |
| Mackenzie DataStream | https://mackenziedatastream.ca/#/page/terms-of-use |
| Capital (Regional District) | https://www.crd.bc.ca/copyright-disclaimer-privacy |
| Friends of Tod Creek Watershed | N/A |
| BC ENV - Real-time Water Data Reporting | https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc |

If a data source is ever down, this list will have the data source provider. Please contact them through here to resolve the issue.

The `watershed` module's data must be calculated from a collection of data. This process will be further explained in the [Calculate fundamental watershed attributes for other components for the reports](#calculate-fundamental-watershed-attributes-for-other-components-for-the-reports) section.

## Data refresh/update processes

The data in the database is updated every day through scrapers that are orchestrated using Apache Airflow. These scrapers are located in the `airflow/etl_pipelines/` directory.

In addition to the daily scrapers, there are quarterly scrapers that ensure that all data available for their respective network are in the database. The networks that have quarterly scrapers are:
- Environment and Climate Change Canada (Hydat)
- Environment and Climate Change Canada (Water Quality)
- Ministry of Environment (Ground Water Wells)
- Ministry of Environment (Historical Hydrometric Data)
- Meteorological Service of Canada (Cliamte)
- BC Environmental Monitoring System (Water Quality)

The quarterly scrapers are also orchestrated by Apache Airflow.

Most of the above scrapers only affect the modules that is not the `Watershed` module.

The scrapers that affect the `Watershed` module are the following:
- DataBC (Water Rights Approval Public)
- DataBC (Water Rights Licences Public)
- DataBC (Water Approval Points)
- BC-ER (Short Term Usage Agreements)

These represent the points (Allocations) that are shown on the map, and are updated on a daily basis.

The other data shown in the `Watershed` module is not affected because they use pre-computed data to generate the reports.

## Procedures for handling broken connections and associated fixes

There is no systematic way of dealing with a error with the scrapers. Most of the issues require a case by case analysis to determine what cause the scrapers to fail. Following are common cases that may happen:

1. Primary key conflict in the destination database table\
    **Error**:
    ```psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "station_observation_pkey"
    DETAIL: Key (station_id, variable_id, datestamp)=(420, 3, 2025-08-03) already exists.
    ```
    This indicates that the database already contained a primary key that is the same as the one that is being inserted.

    **Solution**:
    This indicates that the insertion function does not have a `ON CONFLICT DO` clause. This cann be confirmed to the location that the insertion happened, and finding a variable called `query`. Add either of the following to the query:
    - `ON CONFLICT (station_id, variable_id, datestamp) DO NOTHING`
    - `ON CONFLICT (station_id, variable_id, datestamp) DO UPDATE SET value = EXCLUDED.value`

    The former will not change anything, and just ignore the new value trying to be inserted. The latter will replace the old value with the new.

    Of course, this is just one case, and can happen with other tables, but the above solution can be adapted for any table.

2. Failed to Download the Data from Source\
    **Error**:
    ```
    The URL <some_url> failed to download 3 times, moving on to next URL
    ```

    This means that the url was not reachable, or the data source is down. This is a common issue, and depending on when you check, it is possible that the issue is resolved.

    **Solution**:
    First thing to try is re-run the scraper through airflow. If it still fails, investigate manually by navigating through the web to see if you can manually download the data.

    If you can, the you can conclude that something is wrong with the code and start navigating through the code.

    If you cannot, then it is likely an issue on the provider's side. Contact them through either the contact information in the `README.md`, or by using the table in the [Data connections, sources, and agreements with third parties](#data-connections-sources-and-agreements-with-third-parties) section to get to the parent site.

    Note that `gw_moe`, and `flowworks` stations often do not have data, and will fail to download. This is expected, and can be ignored unless all stations fail to download data.

3. Data is not in the expected format/type\
    **Error**:
    ```
    One of the column names in the downloaded dataset is unexpected! Please check and rerun

    OR

    The type of a column in the downloaded data does not match the expected results! Please check and rerun
    ```

    **Solution**:
    This error can be caused by one of the following:

    1. Column(s) in the data got removed, renamed, or added.
    2. The type of the column changed.

    Both of these cases can be fixed by downloading the data that it is scraping and changing the associated `EXPECTED_DTYPE` dictionary in the `constants.py` file located in `airflow/etl_pipelines/utils/`. The dictionary consists of the column name as the key, and the expected `polars` type as the value.

    If the name of the column changed, then please make sure that the correct column name is being used in the `RENAME_DICT` in the same file.

4. Polars Error\
    This specific error does not have a specific error message that will be shown, and will be used as a catch all for any error that Polars throws.

    If the error mentions something about a `Query Plan` and has a long SQL like query along with the error.

    This will be usually raised in the `transform` function of the scrapers and will need to be investigated.

    There is no specific solution to these issues, because of all the possibilities. But the generalized steps for debugging this error is the following:

    1. Replicate the error
    2. Identify the section of the code that is causing the error
        1. If it is a long Polars query, then break it apart into smaller pieces to idenity the part that is causing the error.
    3. Find the specific exception that is being thrown and determine why it is happening by checking each line of code, while referencing the [Polars Documentation](https://docs.pola.rs/api/python/stable/reference/index.html) to ensure that you know what the method does.
    4. Implement the fix and rerun the scraper.

5. Other Errors\
    This is a catch all for any other errors that are not covered by the above.

    If none of the errors seem to fit in to the above categories, here are some ways to help debug the code:
    1. Use Debug Mode:\
    This allows you to step through each line of code and see what is happening. In addition, you can check each variable's value to make sure it is the expected value
    2. Ensure that data provider did not switch units or formats without breaking the verification step.
    3. Run the unit tests for all modules and make sure that they all pass.
    4. Check the logs to see if any warnings are being thrown as well.


If none of the above categories/steps solve the error, and it is an scraper error, then the following steps will allow the user to turn off the DAG until the error is solved:

1. Log in to the Openshift project through the terminal
2. Port-Forward the `airflow-webserver` pod using the following code:
    ```bash
    oc port-forward <airflow-sebserver-pod> 8080:8080
    ```
3. Navigate to `127.0.0.1:8080` in the web browser.
4. Turn off the specific dag by toggling the switch to the left of the page.

And to turn it back on, do the same thing but toggle the switch to be turned on.

## Process for adding a new region to the framework (explicitly included)

A simplified version of the process for adding a new region to the framework will be described in this section. For a more detailed explanation, please refer to the paper:

>Chapman A, Kerr B, Wilford D (2018) A water allocation decision-support model and tool for predictions in ungauged basins in northeast British Columbia. J Am Water Resour Assoc 54 (3): 676–693. [https://doi.org/10.1111/1752-1688.12643](https://onlinelibrary.wiley.com/doi/10.1111/1752-1688.12643)

### Produce hydrology model

The following information is taken from the `HYDROLOGY MODELING` section of the mentioned paper.

#### Annual Water Balance

<ins>Step 1</ins>:\
Ensure that you have the required gridded data for the region that is intended to be added. To be specific, the required data are the following:
- Precipitation (Annual and monthly)
- Temperature (Annual and monthly)
- Evapotranspiration (grids)
- Land cover
- Vegetation
- Digital Elevation Model (DEM)
- Hydrometric Observations for calibration and validation

The measured hydrometric observations should be taken from stations managed by Water Survey of Canada that have the following characteristics:
- Have unregulated flows
- At least 5 years of data
- Station is not on a very large main stem rivers that arise from outside the study area
- Not lake outlet stations
- Not on drainages with man-made controls

For more information on which data was used for the other regions, look at the `DATA` section of the paper.

<ins>Step 2</ins>:\
The model estimates the water balance at each grid cell using the equation:

$$
\begin{equation}
RO_{pred}=P-ET
\end{equation}
$$

Where $RO_{pred}$ is the predicted runoff (mm), $P$ is the annual precipitation (mm), and $ET$ is the annual evapotranspiration (mm).

<ins>Step 3</ins>:\
Generate the watershed for the stations that will be used for observation data. This can be done using the upstream watershed polygons that are generated in a later section.

Using the watershed, get the predicted data for the hydrological model for each station. This can be used to calculate the `Residual` or `Unpredicted` runoff with:

$$
\begin{equation}
RO_{i,resid}=RO_{i,pred}-RO_{i,obs}
\end{equation}
$$

Where $RO_{i,resid}$ is the residual or unpredicted annual run off for watershed $i$, $RO_{i,pred}$ is the predicted annual runoff for watershed $i$, and $RO_{i,obs}$ is the observed annual runoff for watershed $i$.

<ins>Step 4</ins>:\
Split the region that is being added to the framework into the regions specified in the paper:

> Obedkoff, W. 2000. Streamflow in the Omineca-Peace Region. Victoria, BC: British Columbia Ministry of Environment, Lands and
Parks, Resources Inventory Branch.

Page 16 of the PDF.

Apply multivariate regression analysis on the following variables for each region (refer to table 2 of the paper by Chapman et al.):
- Mean Elevation (m)
- Drainage area (km<sup>2</sup>)
- Mean Annual Temperature (°C)
- Mean Annual Precipitation (mm)
- Latitude (UTM Northing)
- Longitude (UTM Easting)

For each region, take the variable with the highest correlation (as seen in the paper)

<ins>Step 5</ins>:\
Using the adjustment values calculated above, combine it to create an adjusted grid of annual modeled runoff incorporating topographic, geographic and climatic factors:

$$
\begin{equation}
RO_{i,adj}=RO_{i,pred}+RO_{i,resid\_regress}
\end{equation}
$$

Where $RO_{i,adj}$ is the adjusted runoff for watershed $i$, $RO_{i,pred}$ is the predicted runoff for watershed $i$, and $RO_{i,resid\_regress}$ is the runoff adjustment (mm) derived from residual analysis. This is the final determination of modeled water balance in the paper by Chapman et al.

<ins>Step 6</ins>:\
Error can be calculated for each watershed using the following:

$$
\begin{equation}
    E_i = 100 \times \frac{(RO_{i,pred}-RO_{i,obs})}{RO_{i,obs}}
\end{equation}
$$

Where $E_i$ is the percent error for watershed $i$, $RO_{i,pred}$ is the predicted runoff for watershed $i$, and $RO_{i,obs}$ is the observed runoff for watershed $i$.

The mean (MBE), median (ME), and mean of the absolute values (MAE) of the error are calculated for each region. In addition, the percentages of watersheds with error values of $\pm20\%$ are calculated.

#### Monthly Runoff

The monthly runoff has strong relation to seasonality of temperature and precipitation. Furthermore, the freshet peak flows vary depending on the characteristics of the watershed (ie, higher elevations have snowmelt peak flows later in spring).

The monthly runoff model was based off of a statistical analysis of the monthly distribution of the runoff for th WSC hydrometric stations, calculated as the percentage of the mean annual runoff:

$$
\begin{equation}
RO\text{-}MONTH_{i,j}=100 \times (\frac{RO\text{-}MONTH_{i,j, obs}}{RO_{i,obs}})
\end{equation}
$$

Where $RO\text{-}MONTH_{i,j}$ is the runoff for month $j$ and watershed $i$, $RO\text{-}MONTH_{i,j,obs}$ is the observed runoff for month $j$ and watershed $i$,and $RO_{i,obs}$ is the observed annual runoff for watershed $i$.

To calculate the monthly runoff for the entire region, a multivariate regression approach was used to estimate monthly runoff for each month using the following candidate variables:
- Mean Watershed Elevation (m)
- Drainage Area (km<sup>2</sup>)
- Mean Monthly Temperature (°C)
- mean Monthly Precipitation (mm)
- Latitude (UTM Northing)
- Longitude (UTM Easting)

Individual regression equations should be produced for each month. Also do not expect all candidate variables to be significant in the model, some months will rely on specific variables more than others.

The coefficients of the monthly regression models need to be applied to the gridded adjusted annual runoff ($RO_{adj}$) to get the adjusted estimations of monthly runoff.

### Translate monthly mean discharge from hydrology model into fundamental units from Freshwater Atlas

From the watershed and stream data that the Freshwater Atlas has, it is possible to create a lookup table that will be used to identify each fundamental watershed in the new region. The `Watershed Feature ID` (WFI) will be the unique value assigned to each watershed piece, and the `FWA Watershed Code` is the code that indicates which river segment of the river is downstream of each watershed, and which watershed is upstream of that river segment.

For each watershed section, the monthly mean discharge can be calculated by intersecting the polygon with the gridded data, and then averaging the values for each month.

Look at the `bcwat_ws.fwa_fund` table for an example of each WFI, and `bcwat_ws.fund_rollup_report` for an example fo the monthly mean discharge values for each WFI upstream.

### Calculate upstream watershed polygons, and lookup tables for every fundamental watershed in the new region

Upstream watershed polygons for each WFI can be created by following the `FWA Watershed Code` upstream through the stream network. For each WFI, there will also be a downstream WFI, which is based on the next major confluence of rivers that is downstream of the original WFI.

The monthly mean hydrology value can be calculated by taking the average of the watersheds collected by finding the upstream watershed. The same goes to the downstream.

For an example take a look at the `bcwat_ws.fund_rollup_report` table in the database.

### Clean to remove holes and multi-part features

Multipart features can be combined in to one piece by doing a spatial union in the collected upstream watersheds. Since the FWA encomapsses all of BC, there should not be any holes, but if there is a whole in the watershed, it is possible to get the outer boundary of the watershed by finding the outer ring of the polygon, then making that in to the watershed polygon.

This can be done in almost any GIS software.

### Calculate fundamental watershed attributes for other components for the reports

The following attributes will be calculated for each fundamental watershed in the new region:

#### Climate

This uses some of future looking modelled data. Like up to 2099, I will ask Ben what to fill this section with once he get's back.

#### Topography

The topography of the watershed can be calculated using the fundamental watersheds and the DEM used to create the hydrological model. The min, max, and mean of the topography should be calaculated, and the percentiles of the topography (ie, % of the watershed of interest that is above x meters) should also be determined and stored.

#### Land Cover

The land cover for each fundamental watershed can be determined using the same land cover and vegetation data that was used to create the hydrological model.
It is important to store the % of each land cover type in the watershed, he values that the watershed reports currently shows are:
- Barren
- Coniferous
- Cropland
- Deciduous
- Developed
- Grassland
- Herb
- Mixed
- Shrub
- Snow / Glacier
- Water
- Wetland
The area that each land cover type can be calculated by multiplying the area of the watershed with the percent coverage.
