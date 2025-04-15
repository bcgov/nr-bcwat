"""
    This is a temporary file to run all the scrapers just to ensure that they all will run.
    Once there are proper implementations of the scrapers (ie not just pass statements in all methods), they should be turned in
    to a DAG for Airflow and be ran through that.
"""

from scrapers.climate import (
    aqn_pcic,
    asp,
    drive_bc,
    ec_xml,
    flnro_pcic,
    msp,
    viu_fern,
    weather_farm_prd
)
from scrapers.licences import (
    water_approval_points,
    water_licences_bcer,
    water_rights_applications_public,
    water_rights_licences_public
)
from scrapers.quarterly import (
    climate_ec_update,
    gw_moe as quarterly_gw_moe,
    hydat_import,
    water_quality_eccc
)
from scrapers.water import (
    env_hydro,
    flow_works,
    gw_moe,
    wsc_hydrometric
)
from utils.constants import logger
import logging

logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(pathname)s - %(funcName)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

observations = [
    aqn_pcic.EnvAqnPcicPipeline(),
    asp.AspPipeline(),
    drive_bc.DriveBcPipeline(),
    ec_xml.EcXmlPipeline(),
    flnro_pcic.FlnroWmbPcicPipeline(),
    msp.MspPipeline(),
    viu_fern.ViuFernPipeline(),
    weather_farm_prd.WeatherFarmPrdPipeline(),
    env_hydro.EnvHydroPipeline(),
    flow_works.FlowWorksPipeline(),
    gw_moe.GwMoePipeline(),
    climate_ec_update.QuarterlyEcUpdatePipeline(),
    quarterly_gw_moe.QuarterlyGwMoe(),
    hydat_import.HydatPipeline(),
    water_quality_eccc.QuarterlyWaterQualityEcccPipeline()
    ]
wsc_hydro = wsc_hydrometric.WscHydrometricPipeline()

databc = [
    water_approval_points.WaterApprovalPointsPipeline(),
    water_licences_bcer.WaterLicencesBCERPipeline(),
    water_rights_licences_public.WaterRightsLicencesPublicPipeline(),
    water_rights_applications_public.WaterRightsApplicationsPublicPipeline()
    ]


for scraper in observations:
    scraper.transform_data()
    scraper.validate_downloaded_data()
    
    scraper.download_data()
    scraper.get_station_list('')

    scraper.load_data()
    scraper.get_downloaded_data()
    scraper.get_transformed_data()

    print(scraper.name)
    print(scraper.source_url)
    print(scraper.destination_tables)
    print(scraper.station_list)


for scraper in databc:
    scraper.transform_data()
    scraper.validate_downloaded_data()

    scraper.download_data()

    scraper.load_data()
    scraper.get_downloaded_data()
    scraper.get_transformed_data()

    print(scraper.name)
    print(scraper.source_url)
    print(scraper.destination_tables)
    print(scraper.databc_layer_name)


wsc_hydro.download_data()
wsc_hydro.transform_data()
wsc_hydro.load_data()
