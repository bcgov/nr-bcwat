import logging
from queries.bcwat_obs_data import (
    variable_query,
    network_query,
    qa_type_query,
    region_query,
    geo_features_query,
    mapsearch2_query,
    operation_type_query,
    station_type_query,
    station_status_query,
    project_query,
    station_query,
    station_region_query,
    station_project_id_query,
    station_type_id_query,
    water_station_variable_query,
    station_year_query,
    climate_station_variable_query,
    station_network_id_query,
    climate_hourly_realtime,
    climate_msp_daily,
    climate_precipitation_realtime,
    climate_snow_amount,
    climate_snow_depth,
    climate_snow_water_equivalent,
    climate_temperature,
    climate_wind,
    flow_metrics_query,
    extreme_flow_query,
    water_level_query,
    water_discharge_query,
    exclude_reason_query,
    exclude_station_year_query,
    ems_location_type_query,
    water_quality_parameter_query,
    water_quality_parameter_grouping_query,
    water_quality_hourly_data,
    water_quality_units,
)
from queries.bcwat_watershed_data import (
    fwa_stream_name_query,
    fwa_stream_name_unique_query,
    fwa_fund_query,
    fwa_union_query,
    fund_rollup_query,
    fund_rollup_report_query,
)
from queries.bcwat_licence_data import (
    licence_ogc_short_term_approvals,
    licence_bc_purpose,
    bc_wls_wrl_wra,
    wls_water_approvals_deanna,
    bc_water_approvals,
    water_management_geoms,
    licence_bc_app_land,
    bc_data_import_date
)


logger = logging.getLogger("data_transfer")

## The dictionary should have the from table name as the key and the to table name as the value.
## If the value of the dict entry is a string, then check all schemas in schema_to_check. If not, grab from the schema wet.
## Don't uncomment the last 6 entries of this dict, else it'll take a while (>30 min I think). This should finish in around 8 mins
bcwat_obs_data = {
    "variables":["variable", variable_query, "bcwat_obs", "joinless"],
    "networks":["network", network_query, "bcwat_obs", "joinless"],
    "qa_type":["qa_type", qa_type_query, "bcwat_obs", "joinless"],
    "regions":["region", region_query, "bcwat_obs", "joinless"],
    "geo_features":["geo_feature", geo_features_query, "bcwat_ws", "joinless"],
    "mapsearch2":["mapsearch2", mapsearch2_query, "bcwat_ws", "joinless"],
    "operation":["operation", operation_type_query, "bcwat_obs", "joinless"],
    "station_type":["station_type", station_type_query, "bcwat_obs", "joinless"],
    "station_status":["station_status", station_status_query, "bcwat_obs", "joinless"],
    "project":["project_id", project_query, "bcwat_obs", "joinless"],
    "stations":["station", station_query, "bcwat_obs", "joinless"],
    "station_project_id":["station_project_id", station_project_id_query, "bcwat_obs", "join"],
    "station_type_id":["station_type_id", station_type_id_query, "bcwat_obs", "join"],
    "water_station_variable":["station_variable", water_station_variable_query, "bcwat_obs", "join"],
    "climate_station_variable":["station_variable", climate_station_variable_query, "bcwat_obs", "join"],
    "station_year":["station_year", station_year_query, "bcwat_obs", "join"],
    "station_network_id":["station_network_id", station_network_id_query, "bcwat_obs", "join"],
    "station_region":["station_region", station_region_query, "bcwat_obs", "join"],
    "climate_hourly_realtime": ["climate_hourly", climate_hourly_realtime, "bcwat_obs", "join"],
    "climate_msp_daily": ["climate_msp", climate_msp_daily, "bcwat_obs", "join"],
    "climate_precipitation_realtime": ["climate_precipitation", climate_precipitation_realtime, "bcwat_obs", "join"],
    "climate_snow_amount": ["climate_snow_amount", climate_snow_amount, "bcwat_obs", "join"],
    "climate_snow_depth": ["climate_snow_depth", climate_snow_depth, "bcwat_obs", "join"],
    "climate_snow_water_equivalent": ["climate_swe", climate_snow_water_equivalent, "bcwat_obs", "join"],
    "climate_temperature": ["climate_temperature", climate_temperature, "bcwat_obs", "join"],
    "climate_wind": ["climate_wind", climate_wind, "bcwat_obs", "join"],
    "flow_metrics": ["flow_metrics", flow_metrics_query, "bcwat_obs", "join"],
    "extreme_flow": ["extreme_flow", extreme_flow_query, "bcwat_obs", "join"],
    "water_level": ["water_level", water_level_query, "bcwat_obs", "join"],
    "water_discharge": ["water_discharge", water_discharge_query, "bcwat_obs", "join"],
    "exclude_reason": ["exclude_reason", exclude_reason_query, "bcwat_obs", "joinless"],
    "exclude_station_year": ["wsc_station_year_exclude", exclude_station_year_query, "bcwat_obs", "join"],
    "ems_location_type": ["water_quality_ems_location_type", ems_location_type_query, "bcwat_obs", "joinless"],
    "water_quality_parameter": ["water_quality_parameter", water_quality_parameter_query, "bcwat_obs", "joinless"],
    "water_quality_parameter_groupings": ["water_quality_parameter_grouping", water_quality_parameter_grouping_query, "bcwat_obs", "joinless"],
    "water_quality_units": ["water_quality_unit", water_quality_units, "bcwat_obs", "joinless"],
    "water_quality_hourly": ["water_quality_hourly", water_quality_hourly_data, "bcwat_obs", "join"],

}

bcwat_licence_data = {
    "ogc_short_term_approvals":["licence_ogc_short_term_approval", licence_ogc_short_term_approvals, "bcwat_lic", "joinless"],
    "bc_purpose":["licence_bc_purpose", licence_bc_purpose, "bcwat_lic", "joinless"],
    "wls_wrl_wra":["bc_wls_wrl_wra", bc_wls_wrl_wra, "bcwat_lic", "joinless"],
    "water_approvals_deanna":["wls_water_approval_deanna", wls_water_approvals_deanna, "bcwat_lic", "joinless"],
    "water_approvals":["bc_wls_water_approval", bc_water_approvals, "bcwat_lic", "joinless"],
    "watmgmt_dist_area_svw": ["water_management_district_area", water_management_geoms, "bcwat_lic", "joinless"],
    "licence_bc_app_land": ["licence_bc_app_land", licence_bc_app_land, "bcwat_lic", "joinless"],
    "import_date": ["bc_data_import_date", bc_data_import_date, "bcwat_lic", "joinless"]
}

bcwat_watershed_data = {
    # "fwa_funds":["fwa_fund", fwa_fund_query, "bcwat_ws"],
    # "fwa_union":["fwa_union", fwa_union_query, "bcwat_ws"],
    # "funds_rollups":["fund_rollup", fund_rollup_query, "bcwat_ws"],
    # "funds_rollups_report":["fund_rollup_report", fund_rollup_report_query, "bcwat_ws"],
    # "fwa_stream_names":["fwa_stream_name", fwa_stream_name_query, "bcwat_ws"],
    # "fwa_stream_names_unique":["fwa_stream_name_unique", fwa_stream_name_unique_query, "bcwat_ws"]
}

climate_var_id_conversion = {
    1:27,
    2:28,
    3:29,
    26:25,
    27:26
}
