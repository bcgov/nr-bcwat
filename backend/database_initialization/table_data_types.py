import polars as pl

variable_dtype = {
    'variable_id': pl.Int64,
    'variable_name': pl.String,
    'variable_description': pl.String,
    'display_name': pl.String,
    'cell_method': pl.String,
    'unit': pl.String
}

network_dtype = {
    'network_id': pl.Int64,
    'network_name': pl.String,
    'licence_link': pl.String,
    'description': pl.String,
    'redistribute': pl.String,
    'provided_qa': pl.String,
    'network_type': pl.String
}

qa_type_dtype = {
    "qa_type_id": pl.Int8,
    "qa_type_name": pl.String
}

region_dtype = {
    'region_id': pl.Int64,
    'region_name': pl.String,
    'region_click_studyarea': pl.String,
    'region_studyarea_allfunds': pl.String
}

operation_dtype = {
    "operation_id": pl.Int8,
    "operation_name": pl.String,
    "description": pl.String
}

station_type_dtype = {
    "type_id": pl.Int8,
    "type_name": pl.String,
    "type_description": pl.String
}

station_status_dtype = {
    "status_id": pl.Int8,
    "status_name": pl.String
}

project_id_dtype = {
    "project_id": pl.Int8,
    "project_name": pl.String,
    "project_geom4326": pl.String
}

symbol_dtype = {
    "symbol_id": pl.Int8,
    "symbol_code": pl.String,
    "description": pl.String
}

station_dtype = {
    'original_id': pl.String,
    'old_station_id': pl.Int64,
    'network_id': pl.Int64,
    'type_id': pl.Int64,
    'station_name': pl.String,
    'stream_name': pl.String,
    'station_description': pl.String,
    'station_status_id': pl.Int64,
    'operation_id': pl.Int64,
    'longitude': pl.Float64,
    'latitude': pl.Float64,
    'geom4326': pl.String,
    'drainage_area': pl.Float64,
    'elevation': pl.Float64,
    'scrape': pl.String,
    'regulated': pl.String,
    'user_flag': pl.String
}

station_project_id_dtype = {
    "station_id": pl.Int8,
    "project_id": pl.Int8
}

water_station_variable_dtype = {

}

climate_station_variable_dtype = {

}

station_year_dtype = {

}

station_region_dtype = {

}

climate_hourly_dtype = {

}

climate_msp_dtype = {

}

precip_station_observation_dtype = {

}

snow_station_observation_dtype = {

}

sd_station_observation_dtype = {

}

swe_station_observation_dtype = {

}

temp_station_observation_dtype = {

}

wind_station_observation_dtype = {

}

flow_metric_dtype = {

}

nwp_flow_metric_dtype = {

}

extreme_flow_dtype = {

}

level_station_observation_dtype = {

}

discharge_station_observation_dtype = {

}

gw_station_observation_dtype = {

}

exclude_reason_dtype = {

}

wsc_station_year_exclude_dtype = {

}

water_quality_ems_location_type_dtype = {

}

water_quality_parameter_grouping_dtype = {

}

water_quality_parameter_dtype = {

}

station_water_quality_parameter_dtype = {

}

water_quality_unit_dtype = {

}

water_quality_hourly_dtype = {

}

licence_ogc_short_term_approval_dtype = {

}

licence_bc_purpose_dtype = {

}

bc_wls_wrl_wra_dtype = {

}

wls_water_approval_deanna_dtype = {

}

bc_wls_water_approval_dtype = {

}

water_management_district_area_dtype = {

}

licence_bc_app_land_dtype = {

}

bc_data_import_date_dtype = {

}

elevation_bookend_dtype = {

}

lake_dtype = {

}

lake_licence_dtype = {

}

fwa_fund_dtype = {

}

fwa_union_dtype = {

}

fund_rollup_report_dtype = {

}

fwa_stream_name_dtype = {

}

fwa_stream_name_unique_dtype = {

}

geo_feature_dtype = {

}

mapsearch2_dtype = {

}

ws_geom_all_report_dtype = {

}

fdc_dtype = {

}

fdc_physical_dtype = {

}

fdc_distance_dtype = {

}
