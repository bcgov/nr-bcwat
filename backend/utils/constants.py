import logging

logger = logging.getLogger('scraper')

wsc_hydrometric_base_url = "https://dd.meteo.gc.ca/{}/WXO-DD/hydrometric/csv/{}/{}/{}_{}_{}_hydrometric.csv"

env_hydro_stage_base_url = "http://www.env.gov.bc.ca/wsd/data_searches/water/Stage.csv"
env_hydro_discharge_base_url = "http://www.env.gov.bc.ca/wsd/data_searches/water/Discharge.csv"

flowworks_base_url = "https://developers.flowworks.com/fwapi/v2/sites/"
flowworks_crd_base_url = "https://developers.flowworks.com/fwapi/v2/sites/"

env_aqn_pcic_base_url = "https://data.pacificclimate.org/data/pcds/lister/raw/ENV-AQN/{}.rsql.ascii?station_observations.time,station_observations.TEMP_MEAN,station_observations.PRECIP_TOTAL&station_observations.time{}"

env_flnro_wmb_pcic_base_url = "https://data.pacificclimate.org/data/pcds/lister/raw/FLNRO-WMB/{}.rsql.ascii?station_observations.time,station_observations.temperature,station_observations.precipitation&station_observations.time{}"
env_flnro_wmb_pcic_base_url_2 = "https://data.pacificclimate.org/data/pcds/lister/raw/FLNRO-WMB/{}.rsql.ascii?station_observations.time,station_observations.precipitation&station_observations.time{}"

ec_xml_base_url = "https://dd.meteo.gc.ca/{}/WXO-DD/observations/xml/{}/yesterday/"

asp_base_urls = [
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/SW.csv",
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/SD.csv",
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/PC.csv",
        "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/TA.csv",
    ]

viu_fern_base_url = "http://viu-hydromet-wx.ca/graph/ws-graph/dataset/{}/y:{}/{}"

weatherfarprd_base_url = "http://www.bcpeaceweather.com/api/WeatherStation/GetHistoricalStationData?StartDate={}&EndDate={}&StationId={}&TimeInterval=day"

msp_base_url = "http://www.env.gov.bc.ca/wsd/data_searches/snow/asws/data/allmss_current.csv"

climate_moti_base_url = "http://www.drivebc.ca/api/weather/observations?format=json"

moe_gw_base_url = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{native_id}-recent.csv"
moe_gw_quarterly_base_url = "http://www.env.gov.bc.ca/wsd/data_searches/obswell/map/data/{native_id}-average.csv"

quarterly_ec_base_url = "https://dd.meteo.gc.ca/{}/WXO-DD/climate/observations/daily/csv/{province.upper()}/climate_daily_BC_{}_{}_P1D.csv"

quarterly_eccc_base_urls = urls = [
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/columbia-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Columbia-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/fraser-river-long-term-water-quality-monitoring-data/Water-Qual-Eau-Fraser-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/peace-athabasca-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Peace-Athabasca-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/pacific-coastal-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Pacific-Coastal-Cote-Pacifique-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/okanagan-similkameen-river-basin-long-term-water-quality-monitoring-data/Water-Qual-Eau-Okanagan-Similkameen-2000-present.csv",
        "https://data-donnees.az.ec.gc.ca/api/file?path=/substances/monitor/national-long-term-water-quality-monitoring-data/lower-mackenzie-river-basin-long-term-water-quality-monitoring-data-canada-s-north/Water-Qual-Eau-Mackenzie-2000-present.csv",
    ]
