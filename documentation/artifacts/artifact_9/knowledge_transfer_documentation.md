# Knowledge Transfer Documentation
This is the documentation for Artifact #9 of the `Deliverable Documentation`

## Contents:
1. [How changes are made to the model](#how-changes-are-made-to-the-model)
2. [Triggers for model updates](#triggers-for-model-updates)
3. [Implmentation process for updates or code fixes](#implmentation-process-for-updates-or-code-fixes)
4. [Historical and current issues relating to BC Water Tools and their resolution](#historical-and-current-issues-relating-to-bc-water-tools-and-their-resolution)
5. [Data connections, sources, and agreements with third parties](#data-connections-sources-and-agreements-with-third-parties)
6. [Data refresh/update processes](#data-refreshupdate-processes)
7. [Procedures for handling broken connections and associated fixes.](#procedures-for-handling-broken-connections-and-associated-fixes)
8. [Process for adding a new region to the framework (explicitly included)](#process-for-adding-a-new-region-to-the-framework-explicitly-included)
    1. [Produce hydrology model](#produce-hydrology-model)
    2. [Translate monthly mean discharge from hydrology model into fundamental units from Freshwater Atlas](#translate-monthly-mean-discharge-from-hydrology-model-into-fundamental-units-from-freshwater-atlas)
    3. [Calculate upstream watershed polygons, and lookup tables for every fundamental watershed in the new region](#calculate-upstream-watershed-polygons-and-lookup-tables-for-every-fundamental-watershed-in-the-new-region)
    4. [Clean to remove holes and multi-part features](#clean-to-remove-holes-and-multi-part-features)
    5. [Calculate fundamental watershed attributes for other components for the reports](#calculate-fundamental-watershed-attributes-for-other-components-for-the-reports)
        1. [Climate](#climate)
        2. [Topography](#topography)
        3. [Vegetation](#vegetation)
        4. [Streamflow](#streamflow)
        5. [Water quality](#water-quality)
        6. [Watersheds](#watersheds)

## How changes are made to the model

## Triggers for model updates

## Implmentation process for updates or code fixes.

Code fixes and updates will be handled by GitHub and the flow that the BC Gov follows for most projects. But major database changes are done differently, and this will be outlined later in this section. The following are the steps for code changes to the ETL pipeline, backend, and frontend:

<ins>Step 1</ins>:\
Create a branch of the repository with the code changes made to the required section.

If this is a data model change, then make the change in a FlyWay migration SQL file in the `nr-bcwat/migrations/sql/` directory, and named in the following format
```
VX.Y.Z__<description>.sql
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

## Data connections, sources, and agreements with third parties.

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
| Alberta River Basins | https://rivers.alberta.ca/ |
| Lake Windemere Ambassadors | N/A |
| Columbia Lake Stewardship Society | N/A |
| Friends of Kootenay Lake | info@friendsofkootenaylake.ca |
| Village of Belcarra | N/A |
| Wasa Lake Land Improvement District | nowellberg@gmail.com |
| Friends of Swan Creek | https://creativecommons.org/licenses/by-sa/3.0/ |
| ECCC - National Long-term Water Quality Monitoring Data | https://open.canada.ca/en/open-government-licence-canada |
| Mackenzie DataStream | https://mackenziedatastream.ca/#/page/terms-of-use |
| Coastal Hydrology & Climate Change Research Lab / BC FLNRORD - Forest Ecosystems Research Network | http://viu-hydromet-wx.ca/ |
| Capital (Regional District) | https://www.crd.bc.ca/copyright-disclaimer-privacy |
| Friends of Tod Creek Watershed | N/A |
| BC ENV - Real-time Water Data Reporting | https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc |

If a data source is ever down, this list will have the data source provider. Please contact them through here to resolve the issue.
## Data refresh/update processes.

## Procedures for handling broken connections and associated fixes.

## Process for adding a new region to the framework (explicitly included)

### Produce hydrology model

### Translate monthly mean discharge from hydrology model into fundamental units from Freshwater Atlas

### Calculate upstream watershed polygons, and lookup tables for every fundamental watershed in the new region

### Clean to remove holes and multi-part features

### Calculate fundamental watershed attributes for other components for the reports

#### Climate

#### Topography

#### Vegetation

#### Streamflow

#### Water quality

#### Watersheds
