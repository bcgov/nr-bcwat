from flask import Blueprint, request, current_app as app, send_file
from utils.watershed import (
    build_climate_chart_data,
    generate_future_hydrologic_variability,
    unpack_candidate_metadata,
    generate_hydrologic_variability,
    post_process_bus_stops,
    build_fwa_list
)
import json
import polars as pl
import polars_st as st
import shutil
import os
import zipfile
from io import BytesIO
import io as io
import csv as csv

watershed = Blueprint('watershed', __name__)

@watershed.route('/', methods=['GET'])
def get_watershed_by_lat_lng():
    """
    Computes Nearest Watershed by Map Click.

    Query Parameters:
        lat (float): Latitude (required)
        lng (float): Longitude (required)
    """
    lat = request.args.get('lat')
    lng = request.args.get('lng')

    if lat is None or lng is None:
        return {
            "error": "Missing required query parameters 'lat' and/or 'lng'."
        }, 400

    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return {
            "error": "'lat' and 'lng' must be valid float numbers."
        }, 400

    nearest_watershed = app.db.get_watershed_by_lat_lng(lat=lat, lng=lng)

    if nearest_watershed is None:
        # No Watershed Found, and user may be clicking outside of area
        return {
            "wfi": None,
            "geojson": None,
            "name": None
        }, 404

    return {
        "wfi": nearest_watershed['wfi'],
        "geojson": nearest_watershed['geojson'],
        "name": nearest_watershed["name"]
    }, 200

@watershed.route('/licences', methods=['GET'])
def get_watershed_licences():
    """
        Returns all licences within Watershed Module
    """

    watershed_features = app.db.get_watershed_licences()

    # Prevent Undefined Error on FrontEnd
    if watershed_features['geojson']['features'] is None:
        watershed_features['geojson']['features'] = []

    return {
            "type": "FeatureCollection",
            "features": watershed_features['geojson']['features']
            }, 200

@watershed.route('/licences/search', methods=['GET'])
def get_watershed_licences_by_search_term():
    """
    Get Watershed Licence by Search.

    Query Parameters:
        licence_no (string): licence_no
    """
    # Needed for ILIKE search
    licence_no = request.args.get('licence_no')

    if licence_no is None:
        return {
            "error": "Missing required query parameters 'licence_no'"
        }, 400

    licence_no = licence_no + '%'

    matching_licences = app.db.get_watershed_licences_by_search_term(licence_no=licence_no)

    if not len(matching_licences):
        return {
            "results": []
        }, 404

    return {
        "results": matching_licences
    }, 200

@watershed.route("/location/search", methods=['GET'])
def get_place_by_name():
    """
    Get Place by Search.

    Query Parameters:
        location_name (string): location_name
    """
    # Needed for ILIKE search
    location_name = request.args.get('location_name')

    if location_name is None:
        return {
            "error": "Missing required query parameters 'location_name'"
        }, 400

    location_name =  '%' + location_name + '%'

    matching_places = app.db.get_place_by_name(location_name=location_name)

    if not len(matching_places):
        return {
            "results": []
        }, 404

    return {
        "results": matching_places
    }, 200

@watershed.route('/search', methods=['GET'])
def get_watersheds_by_search_term():
    """
    Get Watershed by Search.

    Query Parameters:
        wfi (string): watershed_feature_id
    """
    # Needed for ILIKE search
    wfi = request.args.get('wfi')

    if wfi is None:
        return {
            "error": "Missing required query parameters 'wfi'"
        }, 400

    matching_watersheds = app.db.get_watershed_by_search_term(watershed_feature_id=int(wfi))

    if not len(matching_watersheds):
        return {
            "results": []
        }, 404

    return {
        "results": matching_watersheds
    }, 200

@watershed.route('/<int:id>', methods=['GET'])
def get_watershed_by_id(id):
    """
    Computes Nearest Watershed by Map Click.

    Query Parameters:
        id (int) Watershed Feature Id
    """

    watershed = app.db.get_watershed_by_id(watershed_feature_id=id)

    if watershed is None:
        # No Watershed Found
        return {
            "wfi": None,
            "geojson": None,
            "name": None
        }, 404

    return {
        "wfi": watershed['wfi'],
        "geojson": watershed['geojson'],
        "name": watershed["name"]
    }, 200

@watershed.route('/<int:id>/report', methods=['GET'])
def get_watershed_report_by_id(id):
    """
        Computes Watershed Metrics for Station ID.

        Path Parameters:
            id (int): Watershed ID.

        Region ID's:
            1 - SWP
            2 - NWP
            3 - Cariboo
            4 - KWT
            5 - NWWT
            6 - OWT
    """

    # Dynamically Build Response Object, with available sections, based upon region.
    response = {
        "sectionsAvailable": {
            "overview": True,
            "introduction": True,
            "annualHydrology": True,
            "monthlyHydrology": True,
            "allocationsByIndustry": True,
            "allocations": True,
            "hydrologicVariability": False,
            "futureHydrologicVariability": False,
            "landcover": True,
            "climate": True,
            "topography": True,
            "notes": True,
            "references": True,
            "methods": True
        }
    }

    region_id = app.db.get_watershed_region_by_id(watershed_feature_id=id)['region_id']
    response["regionalId"] = region_id

    watershed_metadata = app.db.get_watershed_report_by_id(watershed_feature_id=id, region_id=region_id)
    fwa_string = app.db.get_watershed_fwa_by_id(watershed_feature_id=id)['fwa_watershed_code']
    fwa_string_list = build_fwa_list(fwa_string)
    bus_stop_names = app.db.get_watershed_bus_stops_by_ids(fwa_watershed_codes=fwa_string_list)
    try:
        post_processed_bus_stop_names = post_process_bus_stops(bus_stop_names)
    except ValueError as e:
        return {
            "error": "No found FWA id for the selected watershed. Please try a different watershed."
        }, 500

    if(not "watershed_metadata" in watershed_metadata.keys() or watershed_metadata["watershed_metadata"] is None):
        return response, 404

    mgmt_basin_name = watershed_metadata.get("watershed_metadata", {}).get("downstream_gnis_name") or "Unnamed Basin"

    response["overview"] = {
          "watershedName": watershed_metadata["watershed_name"],
          "busStopNames": post_processed_bus_stop_names,
          "ppt_mon_hist": watershed_metadata.get("watershed_metadata", {}).get("ppt_monthly_hist", []),
          "ppt_mon_fut_max": watershed_metadata.get("watershed_metadata", {}).get("ppt_monthly_future_max", []),
          "ppt_mon_fut_min": watershed_metadata.get("watershed_metadata", {}).get("ppt_monthly_future_min", []),
          "tave_mon_hist": watershed_metadata.get("watershed_metadata", {}).get("tave_monthly_hist", []),
          "tave_mon_fut_max": watershed_metadata.get("watershed_metadata", {}).get("tave_monthly_future_max", []),
          "tave_mon_fut_min": watershed_metadata.get("watershed_metadata", {}).get("tave_monthly_future_min", []),
          "pas_mon_hist": watershed_metadata.get("watershed_metadata", {}).get("pas_monthly_hist", []),
          "pas_mon_fut_max": watershed_metadata.get("watershed_metadata", {}).get("pas_monthly_future_max", []),
          "pas_mon_fut_min": watershed_metadata.get("watershed_metadata", {}).get("pas_monthly_future_min", []),
          "shrub": watershed_metadata["watershed_metadata"]["shrub"],
          "grassland": watershed_metadata["watershed_metadata"]["grassland"],
          "coniferous": watershed_metadata["watershed_metadata"]["coniferous"],
          "water": watershed_metadata["watershed_metadata"]["water"],
          "snow": watershed_metadata["watershed_metadata"]["snow"],
          "developed": watershed_metadata["watershed_metadata"]["developed"],
          "wetland": watershed_metadata["watershed_metadata"]["wetland"],
          "herb": watershed_metadata["watershed_metadata"]["herb"],
          "deciduous": watershed_metadata["watershed_metadata"]["deciduous"],
          "mixed": watershed_metadata["watershed_metadata"]["mixed"],
          "barren": watershed_metadata["watershed_metadata"]["barren"],
          "cropland": watershed_metadata["watershed_metadata"]["cropland"],
          "elevs": watershed_metadata["watershed_metadata"]["elevs"],
          "mad_m3s": watershed_metadata["watershed_metadata"]["mad_m3s"],
          "area_km2": watershed_metadata["watershed_metadata"]["watershed_area_km2"],
          "max_elev": watershed_metadata["watershed_fdc_data"]["max_elev"] if watershed_metadata["watershed_fdc_data"] else None,
          "avg_elev": watershed_metadata["watershed_fdc_data"]["avg_elev"] if watershed_metadata["watershed_fdc_data"] else None,
          "min_elev": watershed_metadata["watershed_fdc_data"]["min_elev"] if watershed_metadata["watershed_fdc_data"] else None,
          "mgmt_lng": watershed_metadata["watershed_metadata"]["mgmt_lng"],
          "mgmt_lat": watershed_metadata["watershed_metadata"]["mgmt_lat"],
          "mgmt_name": mgmt_basin_name,
          "downstream_area": watershed_metadata["watershed_metadata"]["downstream_area_km2"],
          "query_polygon": json.loads(watershed_metadata["watershed_geom_4326"]),
          "mgmt_polygon": json.loads(watershed_metadata["downstream_geom_4326"]),
      }

    climate_chart_data = build_climate_chart_data(watershed_metadata)
    response['climateChartData'] = climate_chart_data

    if region_id == 4:
        hydrologic_variability_raw = app.db.get_kwt_hydrologic_variability_by_id(watershed_feature_id = id)
        if(hydrologic_variability_raw):
            response['futureHydrologicVariability'] = generate_future_hydrologic_variability(hydrologic_variability_raw['hydrological_variability'])
            response['sectionsAvailable']['futureHydrologicVariability'] = True

    # Handle Candidates/Elevations (OWT/NWWT)
    if region_id == 5 or region_id == 6:

        candidate_metadata_raw = app.db.get_watershed_candidates_by_id(watershed_feature_id=id)
        candidate_metadata_unpacked = unpack_candidate_metadata(query_metadata=watershed_metadata, candidate_metadata=candidate_metadata_raw)

        response["overview"]["elevs_steep"] = watershed_metadata['elevation_steep']
        response["overview"]["elevs_flat"] = watershed_metadata['elevation_flat']

        hydrologic_variability_raw = app.db.get_watershed_hydrologic_variability_by_id(watershed_feature_id=id)
        hydrologic_variability_computed = generate_hydrologic_variability(hydrologic_variability_raw)

        response["hydrologicVariability"] = hydrologic_variability_computed
        response["hydrologicVariabilityMiniMapGeoJson"] = candidate_metadata_unpacked['hydrologicVariabilityMiniMapGeoJson']
        response["hydrologicVariabilityDistanceValues"] = candidate_metadata_unpacked['hydrologicVariabilityDistanceValues']
        response["hydrologicVariabilityClimateData"] = candidate_metadata_unpacked['hydrologicVariabilityClimateData']

        response["sectionsAvailable"]["hydrologicVariability"] = True

    watershed_allocations = app.db.get_watershed_allocations_by_id(watershed_feature_id=id, in_basin='query')
    response["allocations"] = watershed_allocations
    response["overview"]["lic_count"] = pl.DataFrame(watershed_allocations, infer_schema_length = None).select("licence_no").unique().shape[0] if len(watershed_allocations) !=0 else 0

    watershed_industry_allocations = app.db.get_watershed_industry_allocations_by_id(watershed_feature_id=id)
    response["allocationsByIndustry"] = watershed_industry_allocations["results"]

    watershed_monthly_hydrology = app.db.get_watershed_monthly_hydrology_by_id(watershed_feature_id=id, in_basin='query', region_id=region_id)
    response["queryMonthlyHydrology"] = {
        "existingAllocations": watershed_monthly_hydrology["results"]["ea_all"],
        "monthlyDischarge": watershed_monthly_hydrology["results"]["mad_m3s"],
        "rm1": watershed_monthly_hydrology["results"]["risk1"],
        "rm2": watershed_monthly_hydrology["results"]["risk2"],
        "rm3": watershed_monthly_hydrology["results"]["risk3"],
        "meanAnnualDischarge": sum([float(monthly_discharge) for monthly_discharge in watershed_monthly_hydrology["results"]["mad_m3s"]]) / 12,
        "monthlyFlowSensitivities": watershed_monthly_hydrology["results"]["flow_sens"],
        "monthlyDischargePercentages": watershed_monthly_hydrology["results"]["pct_mad"],
        "waterLicenceMonthlyDisplay": watershed_monthly_hydrology["results"]["long_display"],
        "shortTermAllocationMonthlyDisplay": watershed_monthly_hydrology["results"]["short_display"]
      }

    downstream_monthly_hydrology = app.db.get_watershed_monthly_hydrology_by_id(watershed_feature_id=id, in_basin='downstream', region_id=region_id)
    response["downstreamMonthlyHydrology"] = {
        "existingAllocations": downstream_monthly_hydrology["results"]["ea_all"],
        "monthlyDischarge": downstream_monthly_hydrology["results"]["mad_m3s"],
        "rm1": downstream_monthly_hydrology["results"]["risk1"],
        "rm2": downstream_monthly_hydrology["results"]["risk2"],
        "rm3": downstream_monthly_hydrology["results"]["risk3"],
        "meanAnnualDischarge": sum([float(monthly_discharge) for monthly_discharge in downstream_monthly_hydrology["results"]["mad_m3s"]]) / 12,
        "monthlyFlowSensitivities": downstream_monthly_hydrology["results"]["flow_sens"],
        "monthlyDischargePercentages": downstream_monthly_hydrology["results"]["pct_mad"],
        "waterLicenceMonthlyDisplay": downstream_monthly_hydrology["results"]["long_display"],
        "shortTermAllocationMonthlyDisplay": downstream_monthly_hydrology["results"]["short_display"]
      }

    annual_hydrology = app.db.get_watershed_annual_hydrology_by_id(watershed_feature_id=id)
    response["annualHydrology"] = annual_hydrology["results"]

    licence_import_dates = app.db.get_licence_import_dates(watershed_feature_id=id)
    response["licenceImportDates"] = licence_import_dates

    return response, 200

@watershed.route('/<int:id>/report/csv', methods=['GET'])
def get_watershed_report_zip_by_id(id):
    sections_param = request.args.get('sections', '')
    requested_sections = set(s.strip() for s in sections_param.split(',') if s.strip()) if sections_param else set()

    region_id = app.db.get_watershed_region_by_id(watershed_feature_id=id)['region_id']

    watershed_metadata = app.db.get_watershed_report_by_id(watershed_feature_id=id, region_id=region_id)

    if not watershed_metadata or not watershed_metadata.get("watershed_metadata"):
        return {"error": "Watershed not found"}, 404

    zip_stream = BytesIO()
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    with zipfile.ZipFile(zip_stream, "w", zipfile.ZIP_DEFLATED) as zip_file:

        if not requested_sections or 'annualHydrology' in requested_sections:
            annual_hydrology = app.db.get_watershed_annual_hydrology_by_id(watershed_feature_id=id)
            if annual_hydrology["results"]:
                readability_map = {
                    'area_km2': 'Area (km²)',
                    'mad_m3s': 'Mean Annual Discharge (MAD, m³/s)',
                    'allocs_m3s': 'Allocations (average, m³/s)',
                    'allocs_pct': 'Allocations (average, % of MAD)',
                    'rr': 'Reserves and Restrictions',
                    'runoff_m3yr': 'Volume Runoff (m³/yr)',
                    'allocs_m3yr': 'Volume Allocations (m³/yr)',
                    'seasonal_sens': 'Seasonal Flow Sensitivity',
                }
                flattened_data = [
                    {
                        "Metric": readability_map[key],
                        "Query Watershed Value": values.get("query"),
                        "Downstream Watershed Value": values.get("downstream")
                    }
                    for key, values in annual_hydrology["results"].items()
                    if isinstance(values, dict)
                ]
                if flattened_data:
                    zip_file.writestr("annual_hydrology.csv", pl.DataFrame(flattened_data).write_csv())

        if not requested_sections or 'monthlyHydrology' in requested_sections:
            query_monthly = app.db.get_watershed_monthly_hydrology_by_id(
                watershed_feature_id=id, in_basin='query', region_id=region_id)
            downstream_monthly = app.db.get_watershed_monthly_hydrology_by_id(
                watershed_feature_id=id, in_basin='downstream', region_id=region_id)
            if query_monthly["results"] or downstream_monthly["results"]:
                query_results = query_monthly["results"]
                downstream_results = downstream_monthly["results"]
                flattened_data = [
                    {
                        "Month": month,
                        "Metric": metric_name,
                        "Query Watershed Value": query_results.get(qk, [])[i] if i < len(query_results.get(qk, [])) else None,
                        "Downstream Watershed Value": downstream_results.get(dk, [])[i] if i < len(downstream_results.get(dk, [])) else None,
                    }
                    for i, month in enumerate(months)
                    for metric_name, qk, dk in [
                        ("Existing Allocations (m³/s)", "ea_all", "ea_all"),
                        ("Monthly Discharge (m³/s)", "mad_m3s", "mad_m3s"),
                    ]
                ]
                zip_file.writestr("monthly_hydrology.csv", pl.DataFrame(flattened_data).write_csv())

        if not requested_sections or 'allocationsByIndustry' in requested_sections:
            industry_allocs = app.db.get_watershed_industry_allocations_by_id(watershed_feature_id=id)
            if industry_allocs["results"]:
                flattened_data = [
                    {
                        "Industry Type": industry,
                        "Surface Water Licence (m³)": allocations.get("sw_long"),
                        "Surface Water STUA (m³)": allocations.get("sw_short"),
                        "Ground Water Licence (m³)": allocations.get("gw_long"),
                        "Ground Water STUA (m³)": allocations.get("gw_short")
                    }
                    for industry, allocations in industry_allocs["results"].items()
                ]
                zip_file.writestr("allocations_by_industry.csv", pl.DataFrame(flattened_data).write_csv())

        if not requested_sections or 'allocations' in requested_sections:
            allocations = app.db.get_watershed_allocations_by_id(watershed_feature_id=id, in_basin='query')
            if allocations:
                zip_file.writestr("allocations.csv", pl.DataFrame(allocations, infer_schema_length=10000).write_csv())

        if not requested_sections or 'hydrologicVariability' in requested_sections:
            if region_id in (5, 6):
                hydrologic_var = app.db.get_watershed_hydrologic_variability_by_id(watershed_feature_id=id)
                if hydrologic_var:
                    rows = [
                        {
                            "Month": months[row["month"] - 1],
                            "Candidate": f"Candidate {cand_num}",
                            "Station": mv.get(f"c{cand_num}"),
                            "10th Percentile (m³/s)": dict(zip(mv.get("percs", []), mv.get(f"q_m3s_c{cand_num}", []))).get(10),
                            "25th Percentile (m³/s)": dict(zip(mv.get("percs", []), mv.get(f"q_m3s_c{cand_num}", []))).get(25),
                            "50th Percentile (m³/s)": dict(zip(mv.get("percs", []), mv.get(f"q_m3s_c{cand_num}", []))).get(50),
                            "75th Percentile (m³/s)": dict(zip(mv.get("percs", []), mv.get(f"q_m3s_c{cand_num}", []))).get(75),
                            "90th Percentile (m³/s)": dict(zip(mv.get("percs", []), mv.get(f"q_m3s_c{cand_num}", []))).get(90),
                        }
                        for row in hydrologic_var
                        for cand_num in range(1, 4)
                        for mv in [row["month_value"]]
                        if mv.get(f"c{cand_num}")
                    ]
                    if rows:
                        zip_file.writestr("hydrologic_variability.csv", pl.DataFrame(rows).write_csv())
                candidate_metadata = app.db.get_watershed_candidates_by_id(watershed_feature_id=id)
                if candidate_metadata:

                    distance_rows = [
                        {
                            "Candidate ID": row["candidate_id"],
                            "Candidate Name": row["candidate_name"],
                            "Area (km²)": row["candidate_area_km2"],
                            "Month": months[month_idx],
                            "Monthly Flow Ratio": row["candidate_month_value"].get(f"month{month_idx+1:02d}"),
                        }
                        for row in candidate_metadata
                        for month_idx in range(12)
                    ]
                    if distance_rows:
                        zip_file.writestr(
                            "hydrologic_variability_candidate_distance_values.csv",
                            pl.DataFrame(distance_rows).write_csv()
                        )

                    climate_rows = [
                        {
                            "Candidate ID": row["candidate_id"],
                            "Candidate Name": row["candidate_name"],
                            "Latitude": row["candidate_climate_data"].get("lat"),
                            "Longitude": row["candidate_climate_data"].get("lon"),
                            "Upstream Area (km²)": row["candidate_climate_data"].get("upstream_area_km2"),
                            "Min Elevation (m)": row["candidate_climate_data"].get("min_elev"),
                            "Avg Elevation (m)": row["candidate_climate_data"].get("avg_elev"),
                            "Max Elevation (m)": row["candidate_climate_data"].get("max_elev"),
                            "Month": months[month_idx],
                            "Precipitation (mm)": row["candidate_climate_data"].get("ppt", [])[month_idx] if month_idx < len(row["candidate_climate_data"].get("ppt", [])) else None,
                            "Mean Temperature (°C)": row["candidate_climate_data"].get("tave", [])[month_idx] if month_idx < len(row["candidate_climate_data"].get("tave", [])) else None,
                            "Snow (mm)": row["candidate_climate_data"].get("pas", [])[month_idx] if month_idx < len(row["candidate_climate_data"].get("pas", [])) else None,
                        }
                        for row in candidate_metadata
                        for month_idx in range(12)
                    ]
                    if climate_rows:
                        zip_file.writestr(
                            "hydrologic_variability_candidate_climate_data.csv",
                            pl.DataFrame(climate_rows).write_csv()
                        )
            elif region_id == 4:
                hydrologic_var = app.db.get_kwt_hydrologic_variability_by_id(watershed_feature_id = id)
                if hydrologic_var:
                    hv = hydrologic_var['hydrological_variability']
                    return_periods = [6, 20, 50, 80]

                    rows = [
                        {
                            "Month": months[month_idx],
                            "Return Period (years)": rp,
                            "10th Percentile (m³/s)": hv.get(f"nc_p10_m{month_idx+1:02d}_{rp:02d}"),
                            "25th Percentile (m³/s)": hv.get(f"nc_p25_m{month_idx+1:02d}_{rp:02d}"),
                            "50th Percentile (m³/s)": hv.get(f"nc_p50_m{month_idx+1:02d}_{rp:02d}"),
                            "75th Percentile (m³/s)": hv.get(f"nc_p75_m{month_idx+1:02d}_{rp:02d}"),
                            "90th Percentile (m³/s)": hv.get(f"nc_p90_m{month_idx+1:02d}_{rp:02d}"),
                        }
                        for month_idx in range(12)
                        for rp in return_periods
                    ]

                    if rows:
                        zip_file.writestr("future_hydrologic_variability.csv", pl.DataFrame(rows).write_csv())


        if not requested_sections or 'climate' in requested_sections:
            climate_data = watershed_metadata.get("watershed_metadata", {})
            if climate_data:
                flattened_data = [
                    {
                        "Month": month,
                        "Precipitation (mm) historical": climate_data.get("ppt_monthly_hist", [])[i] if i < len(climate_data.get("ppt_monthly_hist", [])) else None,
                        "Precipitation (mm) future high": climate_data.get("ppt_monthly_future_max", [])[i] if i < len(climate_data.get("ppt_monthly_future_max", [])) else None,
                        "Precipitation (mm) future low": climate_data.get("ppt_monthly_future_min", [])[i] if i < len(climate_data.get("ppt_monthly_future_min", [])) else None,
                        "Temperature (°C) historical": climate_data.get("tave_monthly_hist", [])[i] if i < len(climate_data.get("tave_monthly_hist", [])) else None,
                        "Temperature (°C) future high": climate_data.get("tave_monthly_future_max", [])[i] if i < len(climate_data.get("tave_monthly_future_max", [])) else None,
                        "Temperature (°C) future low": climate_data.get("tave_monthly_future_min", [])[i] if i < len(climate_data.get("tave_monthly_future_min", [])) else None,
                        "Snow (mm) historical": climate_data.get("pas_monthly_hist", [])[i] if i < len(climate_data.get("pas_monthly_hist", [])) else None,
                        "Snow (mm) future high": climate_data.get("pas_monthly_future_max", [])[i] if i < len(climate_data.get("pas_monthly_future_max", [])) else None,
                        "Snow (mm) future low": climate_data.get("pas_monthly_future_min", [])[i] if i < len(climate_data.get("pas_monthly_future_min", [])) else None,
                    }
                    for i, month in enumerate(months)
                ]
                zip_file.writestr("climate.csv", pl.DataFrame(flattened_data).write_csv())

        if not requested_sections or 'topography' in requested_sections:
            if region_id in (5, 6):
                df = pl.DataFrame({
                    "Cumulative %": list(range(1, len(watershed_metadata.get("elevation_steep", [])) + 1)),
                    "Elevation Steep (M)": watershed_metadata.get("elevation_steep"),
                    "Elevation Flat (M)": watershed_metadata.get("elevation_flat"),
                })
            else:
                df = pl.DataFrame({
                    "Cumulative %": list(range(1, len(watershed_metadata.get("elevs", [])) + 1)),
                    "Elevation (M)": watershed_metadata.get("elevs"),
                })
            zip_file.writestr("topography.csv", df.write_csv())

    zip_stream.seek(0)
    return send_file(zip_stream, mimetype="application/zip", as_attachment=True,
                     download_name=f"watershed_{id}_report.zip")


@watershed.route('/<int:id>/report/download_watershed/<string:format>', methods=['GET'])
def get_watershed_polygon_as_file(id, format):

    if format not in ("geojson", "shapefile"):
        return {
            "error": "The format value was an unexpected value."
        }, 404

    if not isinstance(id, int) or id < 0:
        return {
            "error": "Invalid watershed id."
        }, 400

    try:
        geom = (
            st.GeoDataFrame(
                data = (
                    pl.DataFrame(app.db.get_watershed_by_id(watershed_feature_id = id))
                    .with_columns(
                    geometry= pl.col("geojson").struct.json_encode()
                    )
                    .drop("geojson")
                    .rows(named=True)
                ),
                geometry_name="geometry",
                geometry_format="geojson"
            )
            .with_columns(
                geometry = pl.col("geometry").st.set_srid(4326)
            )
            .drop("fwa_code")
        )
    except Exception as e:
        raise Exception({
            "user_message": "Error getting the watershed polygon. Please try again later",
            "server_message": e,
            "status_code": 500
        })

    try:
        if format == "geojson":
            zip_stream = BytesIO()

            with zipfile.ZipFile(zip_stream, "w", zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(f"{id}.json", geom.st.write_geojson())

            zip_stream.seek(0)

            response = send_file(
                zip_stream,
                mimetype="application/zip",
                as_attachment=True,
                download_name=f"{id}.zip"
            )
        else:

            id_str = str(id)
            tmp_dir = os.path.join("/tmp", id_str)

            # Clean up existing directory
            if os.path.isdir(tmp_dir):
                shutil.rmtree(tmp_dir)

            # Create directory and write shapefile
            os.makedirs(tmp_dir)
            geom.st.write_file(f"{tmp_dir}/{id_str}.shp")

            # Create zip archive
            zip_path = f"/tmp/{id_str}"
            shutil.make_archive(zip_path, "zip", root_dir=tmp_dir)

            # Send file
            response = send_file(
                f"{zip_path}.zip",
                mimetype="application/zip",
                as_attachment=True,
                download_name=f"{id_str}.zip"
            )

            # Cleanup
            shutil.rmtree(tmp_dir)
            if os.path.exists(f"{zip_path}.zip"):
                os.remove(f"{zip_path}.zip")
    except Exception as e:
        raise Exception({
            "user_message": "Error getting the watershed polygon. Please try again later",
            "server_message": e,
            "status_code": 500
        })

    return response
