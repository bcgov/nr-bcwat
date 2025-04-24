import polars as pl
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


FAIL_RATIO = 0.5

HEADER ={
	"User-Agent": "Foundry Spatial Scraper / Contact me: scrapers@foundryspatial.com",
	"Accept-Encoding": "gzip",
}

MAX_NUM_RETRY = 3

WSC_NAME = "WSC Hydrometric"
WSC_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/hydrometric/csv/BC/daily/BC_daily_hydrometric.csv"
WSC_STATION_SOURCE = "wsc"
WSC_DESTINATION_TABLES = {
    "discharge": "bcwat_obs.water_discharge",
    "level": "bcwat_obs.water_level"
}
WSC_DTYPE_SCHEMA = {
    " ID": pl.String,
    "Date": pl.String,
    "Water Level / Niveau d'eau (m)": pl.Float32,
    "Grade": pl.String,
    "Symbol / Symbole": pl.String,
    "QA/QC": pl.String,
    "Discharge / Débit (cms)": pl.Float32,
    "Grade_duplicated_0": pl.String,
    "Symbol / Symbole_duplicated_0": pl.String,
    "QA/QC_duplicated_0": pl.String
}
WSC_RENAME_DICT = {" ID":"original_id", "Date":"datestamp", "Water Level / Niveau d'eau (m)":"level", "Discharge / Débit (cms)":"discharge"}
WSC_VALIDATE_COLUMNS = [" ID", "Date", "Water Level / Niveau d'eau (m)", "Grade", "Symbol / Symbole", "QA/QC", "Discharge / Débit (cms)", "Grade_duplicated_0", "Symbol / Symbole_duplicated_0", "QA/QC_duplicated_0"]
WSC_VALIDATE_DTYPES = [pl.String, pl.String, pl.Float32, pl.String, pl.String, pl.String, pl.Float32, pl.String, pl.String, pl.String]

ENV_HYDRO_STAGE_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/water/Stage.csv"
ENV_HYDRO_DISCHARGE_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/water/Discharge.csv"

FLOWWORKS_BASE_URL = "https://developers.flowworks.com/fwapi/v2/sites/"
FLOWWORKS_CRD_BASE_URL = "https://developers.flowworks.com/fwapi/v2/sites/"

ENV_AQN_PCIC_BASE_URL = "https://data.pacificclimate.org/data/pcds/lister/raw/ENV-AQN/{}.rsql.ascii?station_observations.time,station_observations.TEMP_MEAN,station_observations.PRECIP_TOTAL&station_observations.time{}"

ENV_FLNRO_WMB_PCIC_BASE_URL = "https://data.pacificclimate.org/data/pcds/lister/raw/FLNRO-WMB/{}.rsql.ascii?station_observations.time,station_observations.temperature,station_observations.precipitation&station_observations.time{}"
ENV_FLNRO_WMB_PCIC_BASE_URL_2 = "https://data.pacificclimate.org/data/pcds/lister/raw/FLNRO-WMB/{}.rsql.ascii?station_observations.time,station_observations.precipitation&station_observations.time{}"

EC_XML_BASE_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/observations/xml/{}/yesterday/"

ASP_BASE_URLS = [
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/SW.csv",
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/SD.csv",
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/PC.csv",
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/TA.csv",
    ]

VIU_FERN_BASE_URL = "http://viu-hydromet-wx.ca/graph/ws-graph/dataset/{}/y:{}/{}"

WEATHERFARPRD_BASE_URL = "http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate={}&EndDate={}&StationId={}&TimeInterval=day"

MSP_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/allmss_current.csv"

CLIMATE_MOTI_BASE_URL = "http://www.drivebc.ca/api/weather/observations?format=json"

MOE_GW_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{native_id}-recent.csv"
MOE_GW_QUARTERLY_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{native_id}-average.csv"

QUARTERLY_EC_BASE_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/climate/observations/daily/csv/{province.upper()}/climate_daily_BC_{}_{}_P1D.csv"

QUARTERLY_ECCC_BASE_URLS = [
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/columbia-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Columbia-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/fraser-river-long-term-water-quality-monitoring-data/Water-Qual-Eau-Fraser-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/peace-athabasca-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Peace-Athabasca-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/pacific-coastal-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Pacific-Coastal-Cote-Pacifique-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/okanagan-similkameen-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Okanagan-Similkameen-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/lower-mackenzie-river-basin-long-term-water-quality-monitoring-data-canada-s-north/Water-Qual-Eau-Mackenzie-2000-present.csv",
    ]
