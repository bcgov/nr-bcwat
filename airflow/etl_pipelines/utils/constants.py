import polars as pl
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

loggers = {}

FAIL_RATIO = 0.5

HEADER ={
    "User-Agent": "Foundry Spatial Scraper / Contact me: scrapers@foundryspatial.com",
    "Accept-Encoding": "gzip",
}

MAX_NUM_RETRY = 3

NEW_STATION_INSERT_DICT_TEMPLATE = {
    "bcwat_obs.station_project_id":["project_id"],
    "bcwat_obs.station_variable":["variable_id"],
    "bcwat_obs.station_year":["year"],
    "bcwat_obs.station_type_id":["type_id"],
    "bcwat_obs.station_network_id":["network_id"]
}

"""
Below this is the scraper specific constants
"""

WSC_NAME = "WSC Hydrometric"
WSC_NETWORK = ["1"]
WSC_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/hydrometric/csv/BC/daily/BC_daily_hydrometric.csv"
WSC_STATION_SOURCE = "wsc"
WSC_DESTINATION_TABLES = {
    "discharge": "bcwat_obs.water_discharge",
    "level": "bcwat_obs.water_level"
}
WSC_DTYPE_SCHEMA = {
    "wsc_daily_hydrometric.csv":{
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
}
WSC_RENAME_DICT = {" ID":"original_id", "Date":"datestamp", "Water Level / Niveau d'eau (m)":"level", "Discharge / Débit (cms)":"discharge"}

MOE_GW_NAME = "MOE Groundwater"
MOE_GW_NETWORK = ["10"]
MOE_GW_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{}-recent.csv"
MOE_GW_QUARTERLY_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{}-average.csv"
MOE_GW_STATION_SOURCE = "gw"
MOE_GW_DESTINATION_TABLES = {"gw_level": "bcwat_obs.ground_water_level"}
MOE_GW_DTYPE_SCHEMA = {
    "station_data": {
        "Time": pl.String,
        "Value": pl.Float64,
        "Approval": pl.String,
        "myLocation": pl.String
    }
}
MOE_GW_RENAME_DICT = {"Time":"datestamp", "Value":"value", "myLocation":"original_id"}

ENV_HYDRO_NAME = "ENV Hydro Stage/Discharge"
ENV_HYDRO_NETWORK = ["53", "28"]
ENV_HYDRO_STAGE_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/water/Stage.csv"
ENV_HYDRO_DISCHARGE_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/water/Discharge.csv"
ENV_HYDRO_STATION_SOURCE = "env-hydro"
ENV_HYDRO_DESTINATION_TABLES = {"discharge": "bcwat_obs.water_discharge", "stage": "bcwat_obs.water_level"}
ENV_HYDRO_DTYPE_SCHEMA = {
    "discharge": {
        "Location ID": pl.String,
        " Location Name": pl.String,
        " Status": pl.String,
        " Latitude": pl.Float64,
        " Longitude": pl.Float64,
        " Date/Time(UTC)": pl.String,
        " Parameter": pl.String,
        " Value": pl.Float64,
        " Unit": pl.String,
        " Grade": pl.String
    },
    "stage":{
        "Location ID": pl.String,
        " Location Name": pl.String,
        " Status": pl.String,
        " Latitude": pl.Float64,
        " Longitude": pl.Float64,
        " Date/Time(UTC)": pl.String,
        " Parameter": pl.String,
        " Value": pl.Float64,
        " Unit": pl.String,
        " Grade": pl.String
    }
}
ENV_HYDRO_RENAME_DICT = {
    "Location ID":"original_id", " Date/Time(UTC)":"datestamp", " Value":"value"
}

FLOWWORKS_NAME = "Flow Works CRD"
FLOWWORKS_BASE_URL = "https://developers.flowworks.com/fwapi/v2/sites/"
FLOWWORKS_TOKEN_URL = "https://developers.flowworks.com/fwapi/v2/tokens"
FLOWWORKS_STATION_SOURCE = "flowworks"
FLOWWORKS_NETWORK = ["3", "50"]
FLOWWORKS_DESTINATION_TABLE = {
    "temperature": "bcwat_obs.climate_temperature",
    "discharge": "bcwat_obs.water_discharge",
    "stage": "bcwat_obs.water_level",
    "swe": "bcwat_obs.climate_swe",
    "pc": "bcwat_obs.climate_precip_amount",
    "rainfall": "bcwat_obs.climate_precip_amount"
}
FLOWWORKS_DTYPE_SCHEMA ={
    "temperature":{
        "DataValue": pl.Float64,
        "DataTime": pl.String
    },
    "discharge":{
        "DataValue": pl.Float64,
        "DataTime": pl.String
    },
    "stage":{
        "DataValue": pl.Float64,
        "DataTime": pl.String
    },
    "swe":{
        "DataValue": pl.Float64,
        "DataTime": pl.String
    },
    "pc":{
        "DataValue": pl.Float64,
        "DataTime": pl.String
    },
    "rainfall":{
        "DataValue": pl.Float64,
        "DataTime": pl.String
    }
}
FLOWWORKS_RENAME_DICT ={
    "DataValue": "value",
    "DataTime": "datestamp"
}
FLOWWORKS_IDEAL_VARIABLES = {
    "discharge": {
        "Preliminary Discharge": 1,
        "unit": "m3/s",
    },
    "stage":{
        "Stage": 7,
        "Water Level (m)": 5,
        "Level": 6,
        "Preliminary Stage": 1,
        "Preliminary Level": 4,
        "Final Level": 3,
        "Final Stage": 2,
        "unit": "m",
    },
    "temperature":{
        "Temperature": 1, 
        "unit": "\xb0C"
    },
    "swe": {
        "SWE": 1, 
        "Snow Water Equivalent": 2,
        "unit": "mm"
    },
    "pc":{
        "PC": 1,
        "Precipitation (cumulative)": 2,
        "unit": "mm"
    },
    "rainfall": {
        "Hourly Rainfall": 2,
        "Rainfall": 1,
        "unit": "mm"
    }
}


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

QUARTERLY_EC_BASE_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/climate/observations/daily/csv/{province.upper()}/climate_daily_BC_{}_{}_P1D.csv"

QUARTERLY_ECCC_BASE_URLS = [
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/columbia-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Columbia-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/fraser-river-long-term-water-quality-monitoring-data/Water-Qual-Eau-Fraser-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/peace-athabasca-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Peace-Athabasca-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/pacific-coastal-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Pacific-Coastal-Cote-Pacifique-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/okanagan-similkameen-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Okanagan-Similkameen-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/lower-mackenzie-river-basin-long-term-water-quality-monitoring-data-canada-s-north/Water-Qual-Eau-Mackenzie-2000-present.csv",
    ]

SPRING_DAYLIGHT_SAVINGS = [
        "1918-03-31 02:00",
        "1919-03-30 02:00",
        "1920-03-28 02:00",
        "1921-04-24 02:00",
        "1922-04-30 02:00",
        "1923-04-29 02:00",
        "1924-04-27 02:00",
        "1925-04-26 02:00",
        "1926-04-25 02:00",
        "1927-04-24 02:00",
        "1928-04-29 02:00",
        "1929-04-28 02:00",
        "1930-04-27 02:00",
        "1931-04-26 02:00",
        "1932-04-24 02:00",
        "1933-04-30 02:00",
        "1934-04-29 02:00",
        "1935-04-28 02:00",
        "1936-04-26 02:00",
        "1937-04-25 02:00",
        "1938-04-24 02:00",
        "1939-04-30 02:00",
        "1940-04-28 02:00",
        "1941-04-27 02:00",
        "1942-02-09 02:00",
        "1946-04-28 02:00",
        "1947-04-27 02:00",
        "1948-04-25 02:00",
        "1949-04-24 02:00",
        "1950-04-30 02:00",
        "1951-04-29 02:00",
        "1952-04-27 02:00",
        "1953-04-26 02:00",
        "1954-04-25 02:00",
        "1955-04-24 02:00",
        "1956-04-29 02:00",
        "1957-04-28 02:00",
        "1958-04-27 02:00",
        "1959-04-26 02:00",
        "1960-04-24 02:00",
        "1961-04-30 02:00",
        "1962-04-29 02:00",
        "1963-04-28 02:00",
        "1964-04-26 02:00",
        "1965-04-25 02:00",
        "1966-04-24 02:00",
        "1967-04-30 02:00",
        "1968-04-28 02:00",
        "1969-04-27 02:00",
        "1970-04-26 02:00",
        "1971-04-25 02:00",
        "1972-04-30 02:00",
        "1973-04-29 02:00",
        "1974-01-06 02:00",
        "1975-02-23 02:00",
        "1976-04-25 02:00",
        "1977-04-24 02:00",
        "1978-04-30 02:00",
        "1979-04-29 02:00",
        "1980-04-27 02:00",
        "1981-04-26 02:00",
        "1982-04-25 02:00",
        "1983-04-24 02:00",
        "1984-04-29 02:00",
        "1985-04-28 02:00",
        "1986-04-27 02:00",
        "1987-04-05 02:00",
        "1988-04-03 02:00",
        "1989-04-02 02:00",
        "1990-04-01 02:00",
        "1991-04-07 02:00",
        "1992-04-05 02:00",
        "1993-04-04 02:00",
        "1994-04-03 02:00",
        "1995-04-02 02:00",
        "1996-04-07 02:00",
        "1997-04-06 02:00",
        "1998-04-05 02:00",
        "1999-04-04 02:00",
        "2000-04-02 02:00",
        "2001-04-01 02:00",
        "2002-04-07 02:00",
        "2003-04-06 02:00",
        "2004-04-04 02:00",
        "2005-04-03 02:00",
        "2006-04-02 02:00",
        "2007-03-11 02:00",
        "2008-03-09 02:00",
        "2009-03-08 02:00",
        "2010-03-14 02:00",
        "2011-03-13 02:00",
        "2012-03-11 02:00",
        "2013-03-10 02:00",
        "2014-03-09 02:00",
        "2015-03-08 02:00",
        "2016-03-13 02:00",
        "2017-03-12 02:00",
        "2018-03-11 02:00",
        "2019-03-10 02:00",
        "2020-03-08 02:00",
        "2021-03-14 02:00",
        "2023-03-12 02:00",
        "2024-03-10 02:00",
        "2025-03-09 02:00",
        "2026-03-08 02:00",
        "2027-03-14 02:00",
        "2028-03-12 02:00",
        "2029-03-11 02:00",
    ]
