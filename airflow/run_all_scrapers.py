"""
    This is a temporary file to run all the scrapers just to ensure that they all will run.
    Once there are proper implementations of the scrapers (ie not just pass statements in all methods), they should be turned in
    to a DAG for Airflow and be ran through that.
"""

import os

## Fill these values with the corresponding values for the database.
# os.environ["PGPORT"] =  
# os.environ["PGUSER"] =  
# os.environ["PGPASS"] =  
# os.environ["PGDB"] =
# os.environ["PGHOST"] =

# from etl_pipelines.scrapers.StationObservationPipeline.climate import (
#     aqn_pcic,
#     asp,
#     drive_bc,
#     ec_xml,
#     flnro_pcic,
#     msp,
#     viu_fern,
#     weather_farm_prd
# )
# from etl_pipelines.scrapers.DataBcPipeline.licences import (
#     water_approval_points,
#     water_licences_bcer,
#     water_rights_applications_public,
#     water_rights_licences_public
# )
# from etl_pipelines.scrapers.QuarterlyPipeline.quarterly import (
#     climate_ec_update,
#     gw_moe as quarterly_gw_moe,
#     hydat_import,
#     water_quality_eccc
# )
from etl_pipelines.scrapers.StationObservationPipeline.water import (
#     env_hydro,
#     flow_works,
    gw_moe,
    wsc_hydrometric
)
from etl_pipelines.utils.functions import setup_logging
from etl_pipelines.utils.database import db
import pendulum
import logging

logger = setup_logging('airflow')

# observations = [
#     aqn_pcic.EnvAqnPcicPipeline(),
#     asp.AspPipeline(),
#     drive_bc.DriveBcPipeline(),
#     ec_xml.EcXmlPipeline(),
#     flnro_pcic.FlnroWmbPcicPipeline(),
#     msp.MspPipeline(),
#     viu_fern.ViuFernPipeline(),
#     weather_farm_prd.WeatherFarmPrdPipeline(),
#     env_hydro.EnvHydroPipeline(),
#     flow_works.FlowWorksPipeline(),
#     climate_ec_update.QuarterlyEcUpdatePipeline(),
#     quarterly_gw_moe.QuarterlyGwMoe(),
#     hydat_import.HydatPipeline(),
#     water_quality_eccc.QuarterlyWaterQualityEcccPipeline()
#     ]
wsc_hydro = wsc_hydrometric.WscHydrometricPipeline(db_conn=db.conn, date_now=pendulum.now("UTC"))
gw_scraper = gw_moe.GwMoePipeline(db_conn=db.conn, date_now=pendulum.now("UTC"))

# databc = [
#     water_approval_points.WaterApprovalPointsPipeline(),
#     water_licences_bcer.WaterLicencesBCERPipeline(),
#     water_rights_licences_public.WaterRightsLicencesPublicPipeline(),
#     water_rights_applications_public.WaterRightsApplicationsPublicPipeline()
#     ]


# for scraper in observations:
#     scraper.transform_data()
#     scraper.validate_downloaded_data()
    
#     scraper.download_data()
#     scraper.get_station_list()

#     scraper.load_data()
#     scraper.get_downloaded_data()
#     scraper.get_transformed_data()

#     print(scraper.name)
#     print(scraper.source_url)
#     print(scraper.destination_tables)
#     print(scraper.station_list)


# for scraper in databc:
#     scraper.transform_data()
#     scraper.validate_downloaded_data()

#     scraper.download_data()

#     scraper.load_data()
#     scraper.get_downloaded_data()
#     scraper.get_transformed_data()

#     print(scraper.name)
#     print(scraper.source_url)
#     print(scraper.destination_tables)
#     print(scraper.databc_layer_name)


wsc_hydro.download_data()
wsc_hydro.validate_downloaded_data()
wsc_hydro.transform_data()
wsc_hydro.load_data()

gw_scraper.download_data()
gw_scraper.validate_downloaded_data()
gw_scraper.transform_data()
gw_scraper.load_data()
