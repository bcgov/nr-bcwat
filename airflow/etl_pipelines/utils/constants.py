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
    "bcwat_obs.station_year":["year"]
}

EXPECTED_UNITS = ["m3/year", "m3/day", "m3/sec", "Total Flow"]

WATER_QUALITY_PARAMETER_DTYPE = {
    "parameter_id": pl.Int64,
    "parameter_name": pl.String,
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
        "ID": pl.String,
        "Date": pl.String,
        "Water Level / Niveau d'eau (m)": pl.Float64,
        "Grade": pl.String,
        "Symbol / Symbole": pl.String,
        "QA/QC": pl.Int64,
        "Discharge / Débit (cms)": pl.Float64,
        "Grade_duplicated_0": pl.String,
        "Symbol / Symbole_duplicated_0": pl.String,
        "QA/QC_duplicated_0": pl.Int64
        }
}
WSC_RENAME_DICT = {
    "ID":"original_id",
    "Date":"datestamp",
    "Water Level / Niveau d'eau (m)":"level",
    "Discharge / Débit (cms)":"discharge"
}
WSC_MIN_RATIO = {
    "discharge": 0.5,
    "level": 0.5
}

MOE_GW_NAME = "MOE Groundwater"
MOE_GW_NETWORK = ["10"]
MOE_GW_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{}-recent.csv"
MOE_GW_STATION_SOURCE = "gw"
MOE_GW_DESTINATION_TABLES = {
    "gw_level": "bcwat_obs.ground_water_level"
}
MOE_GW_DTYPE_SCHEMA = {
    "station_data": {
        "Time": pl.String,
        "Value": pl.Float64,
        "Approval": pl.String,
        "myLocation": pl.String
    }
}
MOE_GW_RENAME_DICT = {
    "Time":"datestamp",
    "Value":"value",
    "myLocation":"original_id"
}
MOE_GW_MIN_RATIO = {
    "gw_level": 0.5
}

ENV_HYDRO_NAME = "ENV Hydro Stage/Discharge"
ENV_HYDRO_NETWORK = ["53", "28"]
ENV_HYDRO_STAGE_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/water/Stage.csv"
ENV_HYDRO_DISCHARGE_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/water/Discharge.csv"
ENV_HYDRO_STATION_SOURCE = "env-hydro"
ENV_HYDRO_DESTINATION_TABLES = {
    "discharge": "bcwat_obs.water_discharge",
    "stage": "bcwat_obs.water_level"
}
ENV_HYDRO_DTYPE_SCHEMA = {
    "discharge": {
        "Location ID": pl.String,
        "Location Name": pl.String,
        "Status": pl.String,
        "Latitude": pl.Float64,
        "Longitude": pl.Float64,
        "Date/Time(UTC)": pl.String,
        "Parameter": pl.String,
        "Value": pl.Float64,
        "Unit": pl.String,
        "Grade": pl.String
    },
    "stage":{
        "Location ID": pl.String,
        "Location Name": pl.String,
        "Status": pl.String,
        "Latitude": pl.Float64,
        "Longitude": pl.Float64,
        "Date/Time(UTC)": pl.String,
        "Parameter": pl.String,
        "Value": pl.Float64,
        "Unit": pl.String,
        "Grade": pl.String
    }
}
ENV_HYDRO_RENAME_DICT = {
    "Location ID":"original_id",
    "Date/Time(UTC)":"datestamp",
    "Value":"value"
}
ENV_HYDRO_MIN_RATIO = {
    "discharge": 0.5,
    "stage": 0.5
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
    "pc": "bcwat_obs.climate_precipitation",
    "rainfall": "bcwat_obs.climate_precipitation"
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
FLOWWORK_MIN_RATIO = {
    "temperature": 0.5,
    "discharge": 0.5,
    "stage": 0.5,
    "swe": 0.5,
    "pc": 0.5,
    "rainfall": 0.5
}

ASP_NAME = "ASP"
ASP_STATION_SOURCE = "asp"
ASP_NETWORK = ["19"]
ASP_BASE_URLS = {
        "SW": "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/SW.csv",
        "SD": "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/SD.csv",
        "PC": "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/PC.csv",
        "TA": "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/TA.csv",
    }
ASP_DESTINATION_TABLES = {
    "SW": "bcwat_obs.climate_swe",
    "SD": "bcwat_obs.climate_snow_depth",
    "PC": "bcwat_obs.climate_precipitation",
    "TA": "bcwat_obs.climate_temperature"
}
ASP_RENAME_DICT = {
    "DATE(UTC)":"datestamp",
    "value":"value",
    "variable":"original_id"
}
ASP_DTYPE_SCHEMA = {
    "SW": {
        "DATE(UTC)": pl.String,
        "variable": pl.String,
        "value": pl.String,
    },
    "SD": {
        "DATE(UTC)": pl.String,
        "variable": pl.String,
        "value": pl.String,
    },
    "PC": {
        "DATE(UTC)": pl.String,
        "variable": pl.String,
        "value": pl.String,
    },
    "TA": {
        "DATE(UTC)": pl.String,
        "variable": pl.String,
        "value": pl.String,
    },
}
ASP_MIN_RATIO = {
    "SW": 0.5,
    "SD": 0.5,
    "PC": 0.5,
    "TA": 0.5
}

MSP_NAME = "Manual Snow Pillow"
MSP_STATION_SOURCE = "msp"
MSP_NETWORK =["24"]
MSP_BASE_URL = {
    "msp": "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/allmss_current.csv"
}
MSP_DESTINATION_TABLES = {
    "msp":"bcwat_obs.climate_msp"
}
MSP_RENAME_DICT = {
    "Snow Course Name": "station_name",
    "Number": "original_id",
    "Date of Survey": "survey_date",
    "Snow Depth cm": "sd",
    "Water Equiv. mm": "swe",
    "Survey Code": "survey_code",
    "Density %": "percent_density",
    "Survey Period": "survey_period"
}
MSP_DTYPE_SCHEMA = {
    "msp": {
        "Snow Course Name": pl.String,
        "Number": pl.String,
        "Elev. metres": pl.Int64,
        "Date of Survey": pl.String,
        "Snow Depth cm": pl.Int64,
        "Water Equiv. mm": pl.Int64,
        "Survey Code": pl.String,
        "Snow Line Elev. m": pl.Int64,
        "Density %": pl.Int64,
        "Survey Period": pl.String
    }
}
MSP_MIN_RATIO = {
    "msp": 0.5
}

DRIVE_BC_NAME = "Drive BC - Moti"
DRIVE_BC_STATION_SOURCE = "moti"
DRIVE_BC_NETWORK_ID = ["20"]
DRIVE_BC_BASE_URL = {
    "drive_bc": "https://legacy.drivebc.ca/api/weather/observations?format=json"
}
DRIVE_BC_DESTINATION_TABLES = {
    "drive_bc": "bcwat_obs.climate_hourly",
    "daily_precipitation": "bcwat_obs.climate_precipitation",
    "daily_snow_amount": "bcwat_obs.climate_snow_amount",
    "daily_snow_depth": "bcwat_obs.climate_snow_depth",
    "daily_temperature": "bcwat_obs.climate_temperature",
    "daily_wind": "bcwat_obs.climate_wind"
}
DRIVE_BC_RENAME_DICT = {
    "id": "original_id",
    "name": "station_name",
    "date": "datetimestamp",
    "description": "station_description"
}
DRIVE_BC_DTYPE_SCHEMA = {
    "drive_bc": {
        'event': pl.String,
        'id': pl.String,
        'name': pl.String,
        'dataStatus': pl.String,
        'date': pl.String,
        'airTemp': pl.String,
        'windMean': pl.String,
        'windMax': pl.String,
        'windDir': pl.String,
        'roadTemp': pl.String,
        'snowSince': pl.String,
        'snowEnd': pl.String,
        'snowDepth': pl.String,
        'precipLastHr': pl.String,
        'precip': pl.String,
        'received': pl.String,
        'lat': pl.String,
        'lon': pl.String,
        'description': pl.String,
        'elevation': pl.String
    }
}
DRIVE_BC_MIN_RATIO = {
    "drive_bc": 0.5
}
DRIVE_BC_HOURLY_TO_DAILY = {
    "daily_precipitation": {
        "daily_precip": {
            "var_id": [17],
            "start_hour": 0,
            "new_var_id": 27,
            "every_period": "12h",
            "offset": "18h",
            "group_by_type": "max"
        },
    },
    "daily_snow_amount":{
        "daily_snow": {
            "var_id": [13, 14],
            "start_hour": 0,
            "new_var_id": 4,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "sum"
        }
    },
    "daily_snow_depth":{
        "daily_snow_depth": {
            "var_id": [5],
            "start_hour": 0,
            "new_var_id": 5,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "mean"
        }
    },
    "daily_temperature": {
        "daily_mean_temp": {
            "var_id": [7],
            "start_hour": 0,
            "new_var_id":7,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "mean"
        },
        "daily_min_temp": {
            "var_id": [7],
            "start_hour": 0,
            "new_var_id": 8,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "min"
        },
        "daily_max_temp": {
            "var_id": [7],
            "start_hour": 0,
            "new_var_id": 6,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "max"
        },
        "daily_mean_road_temp": {
            "var_id": [12],
            "start_hour": 0,
            "new_var_id": 12,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "mean"
        }
    },
    "daily_wind":{
        "daily_mean_wind": {
            "var_id": [9],
            "start_hour": 0,
            "new_var_id":9,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "mean"
        },
        "daily_max_wind": {
            "var_id": [10],
            "start_hour": 0,
            "new_var_id":10,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "max"
        },
        "daily_mean_direction": {
            "var_id": [11],
            "start_hour": 0,
            "new_var_id":11,
            "every_period": "1d",
            "offset": "0h",
            "group_by_type": "mean"
        }
    }
}

EC_XML_NAME = "EC XML Scraper"
EC_XML_STATON_SOURCE = "datamart"
EC_XML_NETWORK_ID = ["21"]
EC_XML_BASE_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/observations/xml/BC/yesterday/yesterday_bc_{}_e.xml"
EC_XML_DESTINATION_TABLES = {
    "temperature": "bcwat_obs.climate_temperature",
    "precipitation": "bcwat_obs.climate_precipitation",
    "wind": "bcwat_obs.climate_wind",
    "snow_amount": "bcwat_obs.climate_snow_amount"
}
EC_XML_RENAME_DICT = {
    "obs_date_local": "datestamp",
    "climate_stn_num": "original_id"
}
EC_XML_DTYPE_SCHEMA = {
    "station_data": {
        "station_name": pl.String,
        "latitude": pl.String,
        "longitude": pl.String,
        "transport_canada_id": pl.String,
        "obs_date_utc": pl.String,
        "obs_date_local": pl.String,
        "climate_stn_num": pl.String,
        "wmo_stn_num": pl.String,
        "air_temp_yesterday_high": pl.String,
        "air_temp_yesterday_low": pl.String,
        "total_precip": pl.String,
        "rain_amnt": pl.String,
        "snow_amnt": pl.String,
        "wind_spd": pl.String,
        "wind_dir": pl.String
    }
}
EC_XML_MIN_RATIO = {
    "temperature": 0.5,
    "precipitation": 0.5,
    "wind": 0.5,
    "snow_amount": 0.5
}

WEATHER_FARM_PRD_NAME = "BC Peace Agri-Weather Network"
WEATHER_FARM_PRD_STATION_SOURCE = "weatherfarmprd"
WEATHER_FARM_PRD_NETWORK_ID = ["30"]
WEATHER_FARM_PRD_BASE_URL = "http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate={}&EndDate={}&StationId={}&TimeInterval=day"
WEATHER_FARM_PRD_DESTINATION_TABLES = {
    "temperature": "bcwat_obs.climate_temperature",
    "rainfall": "bcwat_obs.climate_precipitation"
}
WEATHER_FARM_PRD_RENAME_DICT = {
    "dateTimeStamp": "datestamp",
}
WEATHER_FARM_PRD_DTYPE_SCHEMA = {
    "station_data": {
        "original_id": pl.String,
        "dateTimeStamp": pl.String,
        "accumPrecip": pl.Float64,
        "ytdPrecip": pl.Float64,
        "rainfall": pl.Float64,
        "humidityOut": pl.Int64,
        "tempMax": pl.Float64,
        "tempMin": pl.Float64,
        "tempAvg": pl.Float64,
        "windChill": pl.Float64,
        "windPrevailDir": pl.Int64,
        "windspeedAvg": pl.Float64,
        "windspeedHigh": pl.Int64,
        "frostFreeDays": pl.Int64
    }
}
WEATHER_FARM_PRD_MIN_RATIO = {
    "temperature": 0.5,
    "rainfall": 0.5
}

ENV_FLNRO_WMB_NAME =  "FLNRO-WMB"
ENV_FLNRO_WMB_STATION_SOURCE = "flnro-wmb"
ENV_FLNRO_WMB_NETWORK_ID = ["16"]
ENV_FLNRO_WMB_BASE_URL = "https://www.for.gov.bc.ca/ftp/HPR/external/!publish/BCWS_DATA_MART/{}/{}.csv"
ENV_FLNRO_WMB_DESTINATION_TABLES = {
    "temperature": "bcwat_obs.climate_temperature",
    "precipitation": "bcwat_obs.climate_precipitation"
}
ENV_FLNRO_WMB_RENAME_DICT = {
    "STATION_CODE": "original_id",
    "DATE_TIME": "datestamp",
    "HOURLY_PRECIPITATION": "precipitation_hourly",
    "HOURLY_TEMPERATURE": "temperature_hourly"
}
ENV_FLNRO_WMB_DTYPE_SCHEMA = {
    "station_data": {
        "STATION_CODE": pl.String,
        "STATION_NAME": pl.String,
        "DATE_TIME": pl.String,
        "HOURLY_PRECIPITATION": pl.Float64,
        "HOURLY_TEMPERATURE": pl.Float64,
        "HOURLY_RELATIVE_HUMIDITY": pl.Int64,
        "HOURLY_WIND_SPEED": pl.Float64,
        "HOURLY_WIND_DIRECTION": pl.Int64,
        "HOURLY_WIND_GUST": pl.Float64,
        "HOURLY_FINE_FUEL_MOISTURE_CODE": pl.Float64,
        "HOURLY_INITIAL_SPREAD_INDEX": pl.Float64,
        "HOURLY_FIRE_WEATHER_INDEX": pl.Float64,
        "PRECIPITATION": pl.Float64,
        "FINE_FUEL_MOISTURE_CODE": pl.Float64,
        "INITIAL_SPREAD_INDEX": pl.Float64,
        "FIRE_WEATHER_INDEX": pl.Float64,
        "DUFF_MOISTURE_CODE": pl.Float64,
        "DROUGHT_CODE": pl.Float64,
        "BUILDUP_INDEX": pl.Float64,
        "DANGER_RATING": pl.Int64,
        "RN_1_PLUVIO1": pl.String,
        "SNOW_DEPTH": pl.Float64,
        "SNOW_DEPTH_QUALITY": pl.String,
        "PRECIP_PLUVIO1_STATUS": pl.Int64,
        "PRECIP_PLUVIO1_TOTAL": pl.Float64,
        "RN_1_PLUVIO2": pl.Float64,
        "PRECIP_PLUVIO2_STATUS": pl.Int64,
        "PRECIP_PLUVIO2_TOTAL": pl.Float64,
        "RN_1_RIT": pl.String,
        "PRECIP_RIT_STATUS": pl.Int64,
        "PRECIP_RIT_TOTAL": pl.Float64,
        "PRECIP_RGT": pl.Float64,
        "SOLAR_RADIATION_LICOR": pl.Int64,
        "SOLAR_RADIATION_CM3": pl.String
    }
}
ENV_FLNRO_WMB_MIN_RATIO = {
    "temperature": 0.5,
    "precipitation": 0.5
}

ENV_AQN_NAME = "ENV-AQN"
ENV_AQN_STATION_SOURCE = "env-aqn"
ENV_AQN_NETWORK_ID = ["18"]
ENV_AQN_BASE_URL = {
    "temperature": "https://www.env.gov.bc.ca/epd/bcairquality/aqo/csv/Hourly_Raw_Air_Data/Meteorological/TEMP.csv",
    "precipitation": "https://www.env.gov.bc.ca/epd/bcairquality/aqo/csv/Hourly_Raw_Air_Data/Meteorological/PRECIP.csv"
}
ENV_AQN_DESTINATION_TABLES = {
    "temperature": "bcwat_obs.climate_temperature",
    "precipitation": "bcwat_obs.climate_precipitation"
}
ENV_AQN_RENAME_DICT = {
    "DATE_PST": "datestamp",
    "RAW_VALUE": "value",
    "PARAMETER": "variable",
    "EMS_ID": "original_id"
}
ENV_AQN_DTYPE_SCHEMA = {
    "temperature": {
        "DATE_PST": pl.String,
        "STATION_NAME": pl.String,
        "RAW_VALUE": pl.Float64,
        "REPORTED_VALUE": pl.Float64,
        "INSTRUMENT": pl.String,
        "UNITS": pl.String,
        "PARAMETER": pl.String,
        "EMS_ID": pl.String,
        "LATITUDE": pl.Float64,
        "LONGITUDE": pl.Float64
    },
    "precipitation": {
        "DATE_PST": pl.String,
        "STATION_NAME": pl.String,
        "RAW_VALUE": pl.Float64,
        "REPORTED_VALUE": pl.Float64,
        "INSTRUMENT": pl.String,
        "UNITS": pl.String,
        "PARAMETER": pl.String,
        "EMS_ID": pl.String,
        "LATITUDE": pl.Float64,
        "LONGITUDE": pl.Float64
    }
}
ENV_AQN_MIN_RATIO = {
    "temperature": 0.5,
    "precipitation": 0.5
}

VIU_FERN_BASE_URL = "http://viu-hydromet-wx.ca/graph/ws-graph/dataset/{}/y:{}/{}"

WAP_NAME = "Water Approval Points"
WAP_LAYER_NAME = "water-approval-points"
WAP_DESTINATION_TABLES = {
    "new_approval": "bcwat_lic.bc_wls_water_approval",
    "deanna_in_management_area": "bcwat_lic.bc_wls_water_approval"
}
WAP_DTYPE_SCHEMA ={
    WAP_LAYER_NAME: {
        "geometry": pl.Binary,
        "water_approval_id": pl.Int64,
        "wsd_region": pl.String,
        "approval_type": pl.String,
        "approval_file_number": pl.String,
        "fcbc_tracking_number": pl.Float64,
        "source": pl.String,
        "works_description": pl.String,
        "quantity": pl.String,
        "quantity_units": pl.String,
        "qty_diversion_max_rate": pl.Float64,
        "qty_units_diversion_max_rate": pl.String,
        "water_district": pl.String,
        "precinct": pl.String,
        "latitude": pl.Float64,
        "longitude": pl.Float64,
        "utm_zone": pl.Int64,
        "utm_easting": pl.Int64,
        "utm_northing": pl.Int64,
        "map_sheet": pl.String,
        "approval_status": pl.String,
        "application_date": pl.String,
        "fcbc_acceptance_date": pl.String,
        "approval_issuance_date": pl.String,
        "approval_start_date": pl.String,
        "approval_expiry_date": pl.String,
        "approval_refuse_abandon_date": pl.String,
        "objectid": pl.Int64,
        "se_anno_cad_data": pl.String
    }
}

WRLP_NAME = "Water Rights Licences Public"
WRLP_LAYER_NAME = "water-rights-licences-public"
WRLP_DESTINATION_TABLES = {
    "appurtenant_land": "bcwat_lic.licence_bc_app_land",
    WRLP_LAYER_NAME: "bcwat_lic.bc_water_rights_licences_public"
}
WRLP_DTYPE_SCHEMA = {
    WRLP_LAYER_NAME: {
        'geometry': pl.Binary,
        'wls_wrl_sysid':pl.Int64,
        'pod_number':pl.String,
        'pod_subtype':pl.String,
        'pod_diversion_type':pl.String,
        'pod_status':pl.String,
        'file_number':pl.String,
        'well_tag_number':pl.Float64,
        'licence_number':pl.String,
        'licence_status':pl.String,
        'licence_status_date':pl.String,
        'priority_date':pl.String,
        'expiry_date':pl.String,
        'purpose_use_code':pl.String,
        'purpose_use':pl.String,
        'source_name':pl.String,
        'rediversion_ind':pl.String,
        'quantity':pl.Float64,
        'quantity_units':pl.String,
        'quantity_flag':pl.String,
        'quantity_flag_description':pl.String,
        'qty_diversion_max_rate':pl.Float64,
        'qty_units_diversion_max_rate':pl.String,
        'hydraulic_connectivity':pl.String,
        'permit_over_crown_land_number':pl.String,
        'primary_licensee_name':pl.String,
        'address_line_1':pl.String,
        'address_line_2':pl.String,
        'address_line_3':pl.String,
        'address_line_4':pl.String,
        'country':pl.String,
        'postal_code':pl.String,
        'latitude':pl.Float64,
        'longitude':pl.Float64,
        'district_precinct_name':pl.String,
        'objectid':pl.Int64,
        'se_anno_cad_data':pl.String
    }
}

WRAP_NAME = "Water Rights Applications Public"
WRAP_LAYER_NAME = "water-rights-applications-public"
WRAP_DESTINATION_TABLES = {
    WRAP_LAYER_NAME: "bcwat_lic.bc_water_rights_applications_public",
    "final_table" : "bcwat_lic.bc_wls_wrl_wra"
}
WRAP_DTYPE_SCHEMA = {
    WRAP_LAYER_NAME: {
        "geometry": pl.Binary,
        "wls_wra_sysid": pl.Int64,
        "application_job_number": pl.String,
        "pod_number": pl.String,
        "pod_subtype": pl.String,
        "pod_diversion_type": pl.String,
        "file_number": pl.String,
        "application_status": pl.String,
        "well_tag_number": pl.Float64,
        "purpose_use_code": pl.String,
        "purpose_use": pl.String,
        "qty_diversion_max_rate": pl.Float64,
        "qty_units_diversion_max_rate": pl.String,
        "primary_applicant_name": pl.String,
        "address_line_1": pl.String,
        "address_line_2": pl.String,
        "address_line_3": pl.String,
        "address_line_4": pl.String,
        "country": pl.String,
        "postal_code": pl.String,
        "latitude": pl.Float64,
        "longitude": pl.Float64,
        "district_precinct_name": pl.String,
        "objectid": pl.Int64,
        "se_anno_cad_data": pl.String
    }
}

BC_WLS_WRL_WRA_COLUMN_ORDER = [
    "wls_wrl_wra_id",
    "licence_no",
    "tpod_tag",
    "purpose",
    "pcl_no",
    "qty_original",
    "qty_flag",
    "qty_units",
    "licensee",
    "lic_status_date",
    "priority_date",
    "expiry_date",
    "longitude",
    "latitude",
    "stream_name",
    "quantity_day_m3",
    "quantity_sec_m3",
    "quantity_ann_m3",
    "lic_status",
    "rediversion_flag",
    "flag_desc",
    "file_no",
    "water_allocation_type",
    "pod_diversion_type",
    "geom4326",
    "water_source_type_desc",
    "hydraulic_connectivity",
    "well_tag_number",
    "related_licences",
    "industry_activity",
    "purpose_groups",
    "is_consumptive",
    "ann_adjust",
    "qty_diversion_max_rate",
    "qty_units_diversion_max_rate",
    "puc_groupings_storage"
]

WL_BCER_NAME = "Water Licences BCER"
WL_BCER_URL = "https://data-bc-er.opendata.arcgis.com//datasets/fcc52c0cfb3e4bffb20518880ec36fd0_0.geojson"
WL_BCER_DESTINATION_TABLES = {
    "bcer": "bcwat_lic.licence_ogc_short_term_approval"
}
WL_BCER_DTYPE_SCHEMA = {
    "bcer": {
        "objectid": pl.Int64,
        "pod_number": pl.String,
        "short_term_water_use_num": pl.String,
        "water_source_type": pl.String,
        "water_source_type_desc": pl.String,
        "water_source_name": pl.String,
        "purpose": pl.String,
        "purpose_desc": pl.String,
        "approved_volume_per_day": pl.Float64,
        "approved_total_volume": pl.Int64,
        "approved_start_date": pl.String,
        "approved_end_date": pl.String,
        "status": pl.String,
        "application_determination_num": pl.String,
        "activity_approval_date": pl.String,
        "activity_cancel_date": pl.String,
        "legacy_ogc_file_number": pl.String,
        "proponent": pl.String,
        "authority_type": pl.String,
        "land_type": pl.String,
        "utm_zone": pl.String,
        "utm_northing": pl.Float64,
        "utm_easting": pl.Float64,
        "data_source": pl.String,
        "geom4326": pl.Binary
    }
}

QUARTERLY_EC_NAME = "Quarterly EC Arichive Update"
QUARTERLY_EC_BASE_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/climate/observations/daily/csv/BC/climate_daily_BC_{}_{}_P1D.csv"
QUARTERLY_EC_NETWORK_ID = ["21"]
QUARTERLY_EC_STATION_SOURCE = "datamart"
QUARTERLY_EC_MIN_RATIO = {
    "temperature": 0.5,
    "precipitation": 0.5,
    "snow_depth": 0.5,
    "snow_amount": 0.5
}
QUARTERLY_EC_DESTINATION_TABLES = {
    "temperature": "bcwat_obs.climate_temperature",
    "precipitation": "bcwat_obs.climate_precipitation",
    "snow_depth": "bcwat_obs.climate_snow_depth",
    "snow_amount": "bcwat_obs.climate_snow_amount"
}
# Assuming that they are all strings because there are a lot of empty string values that
# may not be translated well.
QUARTERLY_EC_DTYPE_SCHEMA = {
    "station_data":{
        "Longitude (x)": pl.Float64,
        "Latitude (y)": pl.Float64,
        "Station Name": pl.String,
        "Climate ID": pl.String,
        "Date/Time": pl.String,
        "Year": pl.Int64,
        "Month": pl.Int8,
        "Day": pl.Int8,
        "Data Quality": pl.String,
        "Max Temp (�C)": pl.String,
        "Max Temp Flag": pl.String,
        "Min Temp (�C)": pl.String,
        "Min Temp Flag": pl.String,
        "Mean Temp (�C)": pl.String,
        "Mean Temp Flag": pl.String,
        "Heat Deg Days (�C)": pl.String,
        "Heat Deg Days Flag": pl.String,
        "Cool Deg Days (�C)": pl.String,
        "Cool Deg Days Flag": pl.String,
        "Total Rain (mm)": pl.String,
        "Total Rain Flag": pl.String,
        "Total Snow (cm)": pl.String,
        "Total Snow Flag": pl.String,
        "Total Precip (mm)": pl.String,
        "Total Precip Flag": pl.String,
        "Snow on Grnd (cm)": pl.String,
        "Snow on Grnd Flag": pl.String,
        "Dir of Max Gust (10s deg)": pl.String,
        "Dir of Max Gust Flag": pl.String,
        "Spd of Max Gust (km/h)": pl.String,
        "Spd of Max Gust Flag": pl.String
    }
}
QUARTERLY_EC_RENAME_DICT = {
    "Date/Time": "datestamp",
    "Climate ID": "original_id",
    "Max Temp (�C)": "6",
    "Min Temp (�C)": "8",
    "Mean Temp (�C)": "7",
    "Total Rain (mm)": "29",
    "Total Snow (cm)": "4",
    "Total Precip (mm)": "27",
    "Snow on Grnd (cm)": "5",
}

QUARTERLY_HYDAT_NAME = "Quarterly Hydat Import"
QUARTERLY_HYDAT_BASE_URL = "http://collaboration.cmc.ec.gc.ca/cmc/hydrometrics/www/"
QUARTERLY_HYDAT_STATION_LIST_CSV_URL = "https://dd.meteo.gc.ca/{}/WXO-DD/hydrometric/doc/hydrometric_StationList.csv"
QUARTERLY_HYDATE_NETWORK_ID = ["1"]
QUARTERLY_HYDAT_STATION_SOURCE = "wsc"
QUARTERLY_HYDAT_DESTINATION_TABLES = {
    "FLOW": "bcwat_obs.water_discharge",
    "LEVEL": "bcwat_obs.water_level"
}
# Left Empty since they will not be used
QUARTERLY_HYDAT_MIN_RATIO = {}
QUARTERLY_HYDAT_DTYPE_SCHEMA = {}
QUARTERLY_HYDAT_RENAME_DICT = {}
QUARTERLY_HYDAT_DISCHARGE_LEVEL_QUERIES = {
    "FLOW": """SELECT DLY_FLOWS.STATION_NUMBER,"YEAR","MONTH","FLOW1","FLOW_SYMBOL1","FLOW2","FLOW_SYMBOL2","FLOW3","FLOW_SYMBOL3","FLOW4","FLOW_SYMBOL4","FLOW5","FLOW_SYMBOL5","FLOW6","FLOW_SYMBOL6","FLOW7","FLOW_SYMBOL7","FLOW8","FLOW_SYMBOL8","FLOW9","FLOW_SYMBOL9","FLOW10","FLOW_SYMBOL10","FLOW11","FLOW_SYMBOL11","FLOW12","FLOW_SYMBOL12","FLOW13","FLOW_SYMBOL13","FLOW14","FLOW_SYMBOL14","FLOW15","FLOW_SYMBOL15","FLOW16","FLOW_SYMBOL16","FLOW17","FLOW_SYMBOL17","FLOW18","FLOW_SYMBOL18","FLOW19","FLOW_SYMBOL19","FLOW20","FLOW_SYMBOL20","FLOW21","FLOW_SYMBOL21","FLOW22","FLOW_SYMBOL22","FLOW23","FLOW_SYMBOL23","FLOW24","FLOW_SYMBOL24","FLOW25","FLOW_SYMBOL25","FLOW26","FLOW_SYMBOL26","FLOW27","FLOW_SYMBOL27","FLOW28","FLOW_SYMBOL28","FLOW29","FLOW_SYMBOL29","FLOW30","FLOW_SYMBOL30","FLOW31","FLOW_SYMBOL31" FROM DLY_FLOWS INNER JOIN (SELECT station_number FROM STATIONS where prov_terr_state_loc = 'BC') AS bc ON DLY_FLOWS.station_number = bc."station_number";""",
    "LEVEL": """select DLY_LEVELS."STATION_NUMBER","YEAR","MONTH","LEVEL1","LEVEL_SYMBOL1","LEVEL2","LEVEL_SYMBOL2","LEVEL3","LEVEL_SYMBOL3","LEVEL4","LEVEL_SYMBOL4","LEVEL5","LEVEL_SYMBOL5","LEVEL6","LEVEL_SYMBOL6","LEVEL7","LEVEL_SYMBOL7","LEVEL8","LEVEL_SYMBOL8","LEVEL9","LEVEL_SYMBOL9","LEVEL10","LEVEL_SYMBOL10","LEVEL11","LEVEL_SYMBOL11","LEVEL12","LEVEL_SYMBOL12","LEVEL13","LEVEL_SYMBOL13","LEVEL14","LEVEL_SYMBOL14","LEVEL15","LEVEL_SYMBOL15","LEVEL16","LEVEL_SYMBOL16","LEVEL17","LEVEL_SYMBOL17","LEVEL18","LEVEL_SYMBOL18","LEVEL19","LEVEL_SYMBOL19","LEVEL20","LEVEL_SYMBOL20","LEVEL21","LEVEL_SYMBOL21","LEVEL22","LEVEL_SYMBOL22","LEVEL23","LEVEL_SYMBOL23","LEVEL24","LEVEL_SYMBOL24","LEVEL25","LEVEL_SYMBOL25","LEVEL26","LEVEL_SYMBOL26","LEVEL27","LEVEL_SYMBOL27","LEVEL28","LEVEL_SYMBOL28","LEVEL29","LEVEL_SYMBOL29","LEVEL30","LEVEL_SYMBOL30","LEVEL31","LEVEL_SYMBOL31" from DLY_LEVELS INNER JOIN (SELECT station_number FROM STATIONS where prov_terr_state_loc = 'BC') AS bc ON DLY_LEVELS.station_number = bc."station_number";"""
}

QUARTERLY_MOE_GW_NAME = "Quarterly MOE Groundwater Update"
QUARTERLY_MOE_GW_BASE_URL = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{}-average.csv"
QUARTERLY_MOE_GW_DTYPE_SCHEMA = {
    "station_data": {
        "QualifiedTime": pl.String,
        "Value": pl.Float64,
        "myLocation": pl.String
    }
}
QUARTERLY_MOE_GW_RENAME_DICT = {
    "QualifiedTime": "datestamp",
    "Value": "value",
    "myLocation": "original_id"
}
QUARTERLY_MOE_GW_MIN_RATIO = {
    "gw_level": 0.5
}

QUARTERLY_ECCC_NAME = "Environement and Climate Change Canada: Water Quality"
QUARTERLY_ECCC_STATION_SOURCE = "eccc_wq"
QUARTERLY_ECCC_STATION_NETWORK_ID = ["44"]
QUARTERLY_ECCC_DTYPE_SCHEMA = {
    "columbia-river": {
        "SITE_NO": pl.String,
        "DATE_TIME_HEURE": pl.String,
        "FLAG_MARQUEUR": pl.String,
        "VALUE_VALEUR": pl.String,
        "SDL_LDE": pl.Float64,
        "MDL_LDM": pl.String,
        "VMV_CODE": pl.Int32,
        "UNIT_UNITÉ": pl.String,
        "VARIABLE": pl.String,
        "VARIABLE_FR": pl.String,
        "STATUS_STATUT": pl.String,
        "SAMPLE_ID_ÉCHANTILLON": pl.String
    },
    "fraser-river": {
        "SITE_NO": pl.String,
        "DATE_TIME_HEURE": pl.String,
        "FLAG_MARQUEUR": pl.String,
        "VALUE_VALEUR": pl.String,
        "SDL_LDE": pl.Float64,
        "MDL_LDM": pl.String,
        "VMV_CODE": pl.Int32,
        "UNIT_UNITÉ": pl.String,
        "VARIABLE": pl.String,
        "VARIABLE_FR": pl.String,
        "STATUS_STATUT": pl.String,
        "SAMPLE_ID_ÉCHANTILLON": pl.String
    },
    "peace-athabasca": {
        "SITE_NO": pl.String,
        "DATE_TIME_HEURE": pl.String,
        "FLAG_MARQUEUR": pl.String,
        "VALUE_VALEUR": pl.String,
        "SDL_LDE": pl.Float64,
        "MDL_LDM": pl.String,
        "VMV_CODE": pl.Int32,
        "UNIT_UNITÉ": pl.String,
        "VARIABLE": pl.String,
        "VARIABLE_FR": pl.String,
        "STATUS_STATUT": pl.String,
        "SAMPLE_ID_ÉCHANTILLON": pl.String
    },
    "pacific-coastal": {
        "SITE_NO": pl.String,
        "DATE_TIME_HEURE": pl.String,
        "FLAG_MARQUEUR": pl.String,
        "VALUE_VALEUR": pl.String,
        "SDL_LDE": pl.Float64,
        "MDL_LDM": pl.String,
        "VMV_CODE": pl.Int32,
        "UNIT_UNITÉ": pl.String,
        "VARIABLE": pl.String,
        "VARIABLE_FR": pl.String,
        "STATUS_STATUT": pl.String,
        "SAMPLE_ID_ÉCHANTILLON": pl.String
    },
    "okanagan-similkameen": {
        "SITE_NO": pl.String,
        "DATE_TIME_HEURE": pl.String,
        "FLAG_MARQUEUR": pl.String,
        "VALUE_VALEUR": pl.String,
        "SDL_LDE": pl.Float64,
        "MDL_LDM": pl.String,
        "VMV_CODE": pl.Int32,
        "UNIT_UNITÉ": pl.String,
        "VARIABLE": pl.String,
        "VARIABLE_FR": pl.String,
        "STATUS_STATUT": pl.String,
        "SAMPLE_ID_ÉCHANTILLON": pl.String
    },
    "lower-mackenzie": {
        "SITE_NO": pl.String,
        "DATE_TIME_HEURE": pl.String,
        "FLAG_MARQUEUR": pl.String,
        "VALUE_VALEUR": pl.String,
        "SDL_LDE": pl.Float64,
        "MDL_LDM": pl.String,
        "VMV_CODE": pl.Int32,
        "UNIT_UNITÉ": pl.String,
        "VARIABLE": pl.String,
        "VARIABLE_FR": pl.String,
        "STATUS_STATUT": pl.String,
        "SAMPLE_ID_ÉCHANTILLON": pl.String
    },
}
QUARTERLY_ECCC_DESTINATION_TABLES = {
    "columbia-river": "bcwat_obs.water_quality_hourly",
    "fraser-river": "bcwat_obs.water_quality_hourly",
    "peace-athabasca": "bcwat_obs.water_quality_hourly",
    "pacific-coastal": "bcwat_obs.water_quality_hourly",
    "okanagan-similkameen": "bcwat_obs.water_quality_hourly",
    "lower-mackenzie": "bcwat_obs.water_quality_hourly"
}
QUARTERLY_ECCC_RENAME_DICT = {
    "SITE_NO": "original_id",
    "DATE_TIME_HEURE": "datetimestamp",
    "VALUE_VALEUR": "value",
    "UNIT_UNITÉ": "unit_name",
    "VARIABLE": "parameter_name"
}
QUARTERLY_ECCC_BASE_URLS = {
        "columbia-river": "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/columbia-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Columbia-2000-present.csv",
        "fraser-river": "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/fraser-river-long-term-water-quality-monitoring-data/Water-Qual-Eau-Fraser-2000-present.csv",
        "peace-athabasca": "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/peace-athabasca-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Peace-Athabasca-2000-present.csv",
        "pacific-coastal": "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/pacific-coastal-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Pacific-Coastal-Cote-Pacifique-2000-present.csv",
        "okanagan-similkameen": "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/okanagan-similkameen-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Okanagan-Similkameen-2000-present.csv",
        "lower-mackenzie": "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/lower-mackenzie-river-basin-long-term-water-quality-monitoring-data-canada-s-north/Water-Qual-Eau-Mackenzie-2000-present.csv",
    }




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

STR_MONTH_TO_INT_MONTH = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05", "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}

STR_DIRECTION_TO_DEGREES = {
    "N": "0",
    "NNE": "22.5",
    "NE": "45",
    "ENE": "67.5",
    "E": "90",
    "ESE": "112.5",
    "SE": "135",
    "SSE": "157.5",
    "S": "180",
    "SSW": "202.5",
    "SW": "225",
    "WSW": "247.5",
    "W": "270",
    "WNW": "292.5",
    "NW": "315",
    "NNW": "337.5"
}

APPURTENTANT_LAND_REVIEW_MESSAGE = """
A manual review is needed for the BC Water Tool.
The BC water tool has some backend logic that needs to be maintained manually. It has to do with how the licences relate to each other.
To continue to support this logic, when there is a new licence with ''Stream Storage: Non Power'', it has to be reviewed to see if it shares
appurtenant land with any other licences.

Recently, there was a new licence added within the study region with ''Stream Storage: Non-Power'' as a purpose and it has been inserted into the table:
bcwat_lic.licence_bc_app_land

Use the following query to find out which new licence(s) was added:

SELECT * FROM bcwat_lic.licence_bc_app_land where appurtenant_land is NULL;

Use the licence_no field and lookup to see the Appurtenancy. Paste the licence_no into the Licence Number field at the following URL:

https://j200.gov.bc.ca/pub/ams/Default.aspx?PossePresentation=AMSPublic&PosseMenuName=WS_Main&PosseObjectDef=o_ATIS_DocumentSearch

If that doesn't work -- see if another one has been posted here:

https://www2.gov.bc.ca/gov/content/environment/air-land-water/water/water-licensing-rights/water-licences-approvals/water-rights-databases

In the Water Licence Search results - scroll to the far right to get the Appurtenancy field.

Consider the following case - let's say the new licence_no was XX2.
If the Appurtenancy field says something like:
''AS SET OUT IN CONDITIONAL WATER LICENCE  134252.''
You will need to take which licences are mentioned in the field & but them into a specific field called related_licences.
Here is an example: - here is an example of what you would do if the above case

UPDATE water_licences.licence_bc_app_land SET
appurtenant_land = 'AS SET OUT IN CONDITIONAL WATER LICENCE  134252.',
related_licences = '{134252}'::text[]
WHERE licence_no = 'XX2';

Note: There are cases where there are more than one licence mentioned in the Appurtenancy field - in that case, the line would look like this:

UPDATE water_licences.licence_bc_app_land SET
appurtenant_land = 'AS SET OUT IN CONDITIONAL WATER LICENCE  134252.',
related_licences = '{134252, XX20, XX29}'::text[]
WHERE licence_no = 'XX2';

However, if the Appurtenancy field says something like: 'Lot 12 District Lot 591 Cariboo District Plan BCP23447', then you don't need to fill out the related_licences field.
Example:

UPDATE water_licences.licence_bc_app_land SET
appurtenant_land = 'Lot 12 District Lot 591 Cariboo District Plan BCP23447'
WHERE licence_no = 'XX2';
"""

ECCC_WATERQUALITY_NEW_PARAM_MESSAGE = """
When sraping for water quality data from ECCC, there were new parameters found that are not in the Database. Please insert them using the following instructions and rerun the scraper!

1. For each new parameter, find a keyword for the parameter, usually a element, and check which grouping they would be put into by running the following query on the database:
    SELECT * FROM bcwat_obs.water_quality_parameter WHERE parameter_name Ilike '%<keyword>%';
This will give you the grouping_id, if there are multiple, use the one that shows up the most, or try another keyword.

2. Insert each parameter into the database by running the following
    INSERT INTO bcwat_obs.water_quality_parameter(parameter_name, grouping_id, parameter_desc) VALUES (<new_parameter_1>, <number_from_step_1_1>, <keyword_from_step_1_1>), (<new_parameter_2>, <number_from_step_1_2>, <keyword_from_step_1_2>)....;

3. Please rerun the scraper!
"""
