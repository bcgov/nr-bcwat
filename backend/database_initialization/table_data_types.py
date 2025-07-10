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
    "old_station_id": pl.Int64,
    "project_id": pl.Int8
}

station_variable_dtype = {
    "old_station_id": pl.Int64,
    "variable_id": pl.Int64
}

station_year_dtype = {
    "old_station_id": pl.Int64,
    "year": pl.Int64
}

station_region_dtype = {
    "old_station_id": pl.Int64,
    "region_id": pl.Int8
}

climate_hourly_dtype = {
    "old_station_id": pl.Int128,
    "variable_id": pl.Int8,
    "datetimestamp": pl.Datetime,
    "value": pl.Float64,
    "qa_id": pl.Int8
}

climate_msp_dtype = {
    "old_station_id": pl.Int128,
    "variable_id": pl.Int8,
    "survey_period": pl.Date,
    "datestamp": pl.Date,
    "value": pl.Float64,
    "code": pl.String,
    "qa_id": pl.Int8
}

station_observation_dtype = {
    "old_station_id": pl.Int128,
    "variable_id": pl.Int8,
    "datestamp": pl.Date,
    "value": pl.Float64,
    "qa_id": pl.Int8
}

flow_metric_dtype = {
    "old_station_id": pl.Int128,
    "station_flow_metric": pl.String
}

nwp_flow_metric_dtype = {
    "original_id": pl.String,
    "station_flow_metric": pl.String
}

extreme_flow_dtype = {
    "original_id": pl.String,
    "value": pl.Float64,
    "variable_name": pl.String
}

water_station_observation_dtype = {
    "old_station_id": pl.Int128,
    "variable_id": pl.Int8,
    "datestamp": pl.Date,
    "value": pl.Float64,
    "qa_id": pl.Int8,
    "symbol_id": pl.Int8
}

exclude_reason_dtype = {
    "exclude_id": pl.Int8,
    "exclude_description": pl.String
}

wsc_station_year_exclude_dtype = {
    "old_station_id": pl.Int128,
    "exclude_id": pl.Int8,
    "dateyear": pl.Date
}

water_quality_ems_location_type_dtype = {
    "location_type_code": pl.String,
    "location_type_description": pl.String,
    "include": pl.String
}

water_quality_parameter_grouping_dtype = {
    "grouping_id": pl.Int64,
    "grouping_name": pl.String,
    "parent_group": pl.String,
    "child_group": pl.String
}

water_quality_parameter_dtype = {
    "parameter_id": pl.Int64,
    "grouping_id": pl.Int64,
    "parameter_name": pl.String,
    "parameter_desc": pl.String
}

station_water_quality_parameter_dtype = {
    "old_station_id": pl.Int128,
    "parameter_id": pl.Int128
}

water_quality_unit_dtype = {
    "unit_id": pl.Int32,
    "unit_name": pl.String
}

water_quality_hourly_dtype = {
    "old_station_id": pl.Int128,
    "datetimestamp": pl.Datetime,
    "parameter_id": pl.Int32,
    "unit_id": pl.Int32,
    "qa_id": pl.Int32,
    "location_purpose": pl.String,
    "sampling_agency": pl.String,
    "analyzing_agency": pl.String,
    "collection_method": pl.String,
    "sample_state": pl.String,
    "sample_descriptor": pl.String,
    "analytical_method": pl.String,
    "qa_index_code": pl.String,
    "value": pl.Float64,
    "value_text": pl.String,
    "value_letter": pl.String
}

licence_ogc_short_term_approval_dtype = {
    "short_term_approval_id": pl.String,
    "pod_number": pl.String,
    "short_term_water_use_num": pl.String,
    "water_source_type": pl.String,
    "water_source_type_desc": pl.String,
    "water_source_name": pl.String,
    "purpose": pl.String,
    "purpose_desc": pl.String,
    "approved_volume_per_day": pl.Int128,
    "approved_total_volume": pl.Int128,
    "approved_start_date": pl.Date,
    "approved_end_date": pl.Date,
    "status": pl.String,
    "application_determination_num": pl.String,
    "activity_approval_date": pl.Date,
    "activity_cancel_date": pl.Date,
    "legacy_ogc_file_number": pl.String,
    "proponent": pl.String,
    "authority_type": pl.String,
    "land_type": pl.String,
    "data_source": pl.String,
    "geom4326": pl.String,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "is_consumptive": pl.String
}

licence_bc_purpose_dtype = {
    "purpose": pl.String,
    "general_activity_code": pl.String,
    "purpose_name": pl.String,
    "purpose_code": pl.String,
    "purpose_groups": pl.String,
    "is_consumptive": pl.String,
    "puc_groupings_storage": pl.String,
    "pid": pl.Int128,
    "still_used_by_databc": pl.String
}

bc_wls_wrl_wra_dtype = {
    "wls_wrl_wra_id": pl.String,
    "licence_no": pl.String,
    "tpod_tag": pl.String,
    "purpose": pl.String,
    "pcl_no": pl.String,
    "qty_original": pl.Float64,
    "qty_flag": pl.String,
    "qty_units": pl.String,
    "licensee": pl.String,
    "lic_status_date": pl.Date,
    "priority_date": pl.Date,
    "expiry_date": pl.Date,
    "longitude": pl.Float64,
    "latitude": pl.Float64,
    "stream_name": pl.String,
    "quantity_day_m3": pl.Float64,
    "quantity_sec_m3": pl.Float64,
    "quantity_ann_m3": pl.Float64,
    "lic_status": pl.String,
    "rediversion_flag": pl.String,
    "flag_desc": pl.String,
    "file_no": pl.String,
    "water_allocation_type": pl.String,
    "pod_diversion_type": pl.String,
    "geom4326": pl.String,
    "water_source_type_desc": pl.String,
    "hydraulic_connectivity": pl.String,
    "well_tag_number": pl.String,
    "related_licences": pl.List(pl.String),
    "industry_activity": pl.String,
    "purpose_groups": pl.String,
    "is_consumptive": pl.String,
    "ann_adjust": pl.Float64,
    "quantity_ann_m3_storage_adjust": pl.Float64,
    "puc_groupings_storage": pl.String,
    "qty_diversion_max_rate": pl.Float64,
    "qty_units_diversion_max_rate": pl.String
}

wls_water_approval_deanna_dtype = {
    "appfileno": pl.String,
    "proponent": pl.String,
    "podno": pl.String,
    "latitude": pl.Float64,
    "longitude": pl.Float64,
    "purpose": pl.String,
    "sourcetype": pl.String,
    "sourcename": pl.String,
    "fishpresence": pl.String,
    "startdate": pl.Date,
    "expirationdate": pl.Date,
    "ms": pl.Float64,
    "md": pl.Float64,
    "my": pl.Float64,
    "geom4326": pl.String,
    "deanna_id": pl.String,
    "quantity": pl.Float64,
    "quantity_units": pl.String,
    "qty_diversion_max_rate": pl.Float64,
    "qty_units_diversion_max_rate": pl.String,
    "approval_status": pl.String
}

bc_wls_water_approval_dtype = {
        "bc_wls_water_approval_id": pl.String,
        "wsd_region": pl.String,
        "approval_type": pl.String,
        "approval_file_number": pl.String,
        "fcbc_tracking_number": pl.String,
        "source": pl.String,
        "works_description": pl.String,
        "quantity": pl.Float64,
        "quantity_units": pl.String,
        "qty_diversion_max_rate": pl.Float64,
        "qty_units_diversion_max_rate": pl.String,
        "water_district": pl.String,
        "precinct": pl.String,
        "latitude": pl.Float64,
        "longitude": pl.Float64,
        "approval_status": pl.String,
        "application_date": pl.Date,
        "fcbc_acceptance_date": pl.Date,
        "approval_issuance_date": pl.Date,
        "approval_start_date": pl.Date,
        "approval_expiry_date": pl.Date,
        "approval_refuse_abandon_date": pl.Date,
        "geom4326": pl.String,
        "created": pl.Date,
        "proponent": pl.String,
        "podno": pl.String
}

water_management_district_area_dtype = {
    "district_id": pl.Int128,
    "district_name": pl.String,
    "geom4326": pl.String
}

licence_bc_app_land_dtype = {
    "licence_no": pl.String,
    "appurtenant_land": pl.String,
    "related_licences": pl.List(pl.String),
    "fa": pl.String,
    "purpose": pl.List(pl.String)
}

bc_data_import_date_dtype = {
    "dataset": pl.String,
    "import_date": pl.Date
}

elevation_bookend_dtype = {
    "region_id": pl.Int8,
    "elevation_flat": pl.List(pl.Float64),
    "elevation_steep": pl.List(pl.Float64)
}

lake_dtype = {
    "waterbody_poly_id": pl.Int64,
    "geom4326": pl.String,
    "gnis_name": pl.String,
    "area_m2": pl.Float64,
    "fwa_watershed_code": pl.String,
    "local_watershed_code": pl.String,
    "geom4326_buffer_100": pl.String,
    "winter_allocs_m3": pl.Float64
}

lake_licence_dtype = {
    "lake_licence_id": pl.Int64,
    "waterbody_poly_id": pl.String,
    "lake_name": pl.String,
    "licence_stream_name": pl.String
}

fwa_fund_dtype = {
    "watershed_feature_id": pl.Int128,
    "fwa_watershed_code": pl.String,
    "local_watershed_code": pl.String,
    "the_geom": pl.String,
    "centroid": pl.String,
    "lake_name": pl.String,
    "report": pl.Int32,
    "local_watershed_order": pl.Int32,
    "has_upstream": pl.String,
    "in_study_area": pl.String,
    "point_inside_poly": pl.String,
    "lake": pl.String,
    "area": pl.Float32,
    "geom4326": pl.String,
    "point_inside_poly4326": pl.String,
    "pip_x4326": pl.Float64,
    "pip_y4326": pl.Float64,
    "watershed_feature_id_foundry_eca": pl.Int64,
    "has_netcdf": pl.String,
}

fwa_union_dtype = {
    "fwa_watershed_code": pl.String,
    "geom_simp4326": pl.String
}

fund_rollup_report_dtype = {
    "watershed_feature_id": pl.Int128,
    "downstream_id": pl.Int128,
    "watershed_metadata": pl.String,
}

fwa_stream_name_dtype = {
    "linear_feature_id": pl.Int128,
    "fwa_watershed_code": pl.String,
    "gnis_name": pl.String,
    "stream_magnitude": pl.Int64,
    "geom4326": pl.String,
    "point_on_line4326": pl.String,
}

fwa_stream_name_unique_dtype = {
    "fwa_watershed_code": pl.String,
    "gnis_name": pl.String,
}

geo_feature_dtype = {
    "geoname": pl.String,
    "x": pl.Float64,
    "y": pl.Float64,
    "zoom": pl.Int64,
    "geocomment": pl.String,
    "concisecode": pl.String,
    "geom4326": pl.String,
    "dt_imported": pl.Datetime,
}

mapsearch2_dtype = {
    "geoname": pl.String,
    "x": pl.Float64,
    "y": pl.Float64,
    "zoom": pl.Int64,
    "geocomment": pl.String,
    "concisecode": pl.String,
}

ws_geom_all_report_dtype = {
    "watershed_feature_id": pl.Int128,
	"fwa_watershed_code": pl.String,
	"local_watershed_code": pl.String,
	"upstream_geom_4326_z12": pl.String,
	"area_m2": pl.Float64,
	"longitude": pl.Float64,
	"latitude": pl.Float64,
	"gnis_name": pl.String,
	"number_of_points_in_polygon": pl.Int128
}

fdc_dtype = {
    "watershed_feature_id": pl.Int128,
    "month": pl.Int8,
    "month_value": pl.String,
}

fdc_physical_dtype = {
    "watershed_feature_id": pl.Int128,
    "watershed_fdc_data": pl.String,
}

fdc_distance_dtype = {
    "watershed_feature_id": pl.Int128,
    "candidate": pl.String,
    "candidate_month_value": pl.String,
}

fdc_wsc_station_in_model_dtype = {
    "original_id": pl.String,
    "watershed_feature_id": pl.Int128,
    "area_km2": pl.Float64,
    "station_name": pl.String,
    "excluded": pl.String,
    "exclusion_reason": pl.String,
    "wfi_fake": pl.Int128,
    "geom4326": pl.String
}
