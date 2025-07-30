from flask import Blueprint, request, current_app as app
from utils.shared import write_db_response_to_fixture
from utils.watershed import (
    build_climate_chart_data,
    unpack_candidate_metadata,
    generate_hydrologic_variability
)
import json

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
        # No Watershed Found
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
        wls_id (string): water_licence_id
    """
    # Needed for ILIKE search
    wls_id = request.args.get('wls_id') + '%'

    if wls_id is None:
        return {
            "error": "Missing required query parameters 'wls_id'"
        }, 400

    matching_licences = app.db.get_watershed_licences_by_search_term(water_licence_id=wls_id)

    if not len(matching_licences):
        return {
            "results": []
        }, 404

    return {
        "results": matching_licences
    }, 200

@watershed.route('/search', methods=['GET'])
def get_watersheds_by_search_term():
    """
    Get Watershed by Search.

    Query Parameters:
        wfi (string): watershed_feature_id
    """
    # Needed for ILIKE search
    wfi = request.args.get('wfi') + '%'

    if wfi is None:
        return {
            "error": "Missing required query parameters 'wfi'"
        }, 400

    matching_watersheds = app.db.get_watershed_by_search_term(watershed_feature_id=wfi)

    if not len(matching_watersheds):
        return {
            "results": []
        }, 404

    return {
        "results": matching_watersheds
    }, 200

@watershed.route('/<int:id>/report', methods=['GET'])
def get_watershed_report_by_id(id):
    """
        Computes Watershed Metrics for Station ID.

        Path Parameters:
            id (int): Watershed ID.
    """

    region = app.db.get_watershed_region_by_id(watershed_feature_id=id)
    print(region)
    if region:
        region_id = region['region_id']
    else:
        region_id = -1

    watershed_metadata = app.db.get_watershed_report_by_id(watershed_feature_id=id, region_id=region_id)
    climate_chart_data = build_climate_chart_data(watershed_metadata)

    bus_stops = app.db.get_watershed_bus_stops_by_id(watershed_feature_id=id)

    candidate_metadata_raw = app.db.get_watershed_candidates_by_id(watershed_feature_id=id)
    candidate_metadata_unpacked = unpack_candidate_metadata(candidate_metadata_raw)

    watershed_allocations = app.db.get_watershed_allocations_by_id(watershed_feature_id=id, in_basin='query')

    hydrologic_variability_raw = app.db.get_watershed_hydrologic_variability_by_id(watershed_feature_id=id)
    hydrologic_variability_computed = generate_hydrologic_variability(hydrologic_variability_raw)

    watershed_monthly_hydrology = app.db.get_watershed_monthly_hydrology_by_id(watershed_feature_id=id, in_basin='query', region_id=region_id)

    downstream_monthly_hydrology = app.db.get_watershed_monthly_hydrology_by_id(watershed_feature_id=id, in_basin='downstream', region_id=region_id)

    watershed_industry_allocations = app.db.get_watershed_industry_allocations_by_id(watershed_feature_id=id)

    annual_hydrology = app.db.get_watershed_annual_hydrology_by_id(watershed_feature_id=id)

    licence_import_dates = app.db.get_licence_import_dates(watershed_feature_id=id)

    try:
        return {
        "overview": {
            "watershedName": watershed_metadata["watershed_name"] if watershed_metadata["watershed_name"] is not None else "Unnamed Basin",
            "busStopNames": [bus_stop['name'] for bus_stop in bus_stops],
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
            "mgmt_name": watershed_metadata["watershed_metadata"]["downstream_gnis_name"],
            "downstream_area": watershed_metadata["watershed_metadata"]["downstream_area_km2"],
            "query_polygon": json.loads(watershed_metadata["watershed_geom_4326"]),
            "mgmt_polygon": json.loads(watershed_metadata["downstream_geom_4326"]),
            "lic_count": len({alloc["licence_no"] for alloc in watershed_allocations if "licence_no" in alloc}),
            "elevs_steep": watershed_metadata['elevation_steep'],
            "elevs_flat": watershed_metadata['elevation_flat'],
        },
        "climateChartData": climate_chart_data,
        "allocations": watershed_allocations,
        "allocationsByIndustry": watershed_industry_allocations["results"],
        "hydrologicVariability": hydrologic_variability_computed,
        "hydrologicVariabiltiyMiniMapGeoJson": candidate_metadata_unpacked['hydrologicVariabilityMiniMapGeoJson'],
        "hydrologicVariabilityDistanceValues": candidate_metadata_unpacked['hydrologicVariabilityDistanceValues'],
        "hydrologicVariabilityClimateData": candidate_metadata_unpacked['hydrologicVariabilityClimateData'],
        "queryMonthlyHydrology": {
            "existingAllocations": watershed_monthly_hydrology["results"]["ea_all"],
            "monthlyDischarge": watershed_monthly_hydrology["results"]["mad_m3s"],
            "rm1": watershed_monthly_hydrology["results"]["risk1"],
            "rm2": watershed_monthly_hydrology["results"]["risk2"],
            "rm3": watershed_monthly_hydrology["results"]["risk3"],
            "meanAnnualDischarge": sum([float(monthly_discharge) for monthly_discharge in watershed_monthly_hydrology["results"]["mad_m3s"]]),
            "monthlyFlowSensitivities": watershed_monthly_hydrology["results"]["flow_sens"],
            "monthlyDischargePercentages": watershed_monthly_hydrology["results"]["pct_mad"],
            "waterLicenceMonthlyDisplay": watershed_monthly_hydrology["results"]["long_display"],
            "shortTermAllocationMonthlyDisplay": watershed_monthly_hydrology["results"]["short_display"]
        },
        "downstreamMonthlyHydrology": {
            "existingAllocations": downstream_monthly_hydrology["results"]["ea_all"],
            "monthlyDischarge": downstream_monthly_hydrology["results"]["mad_m3s"],
            "rm1": downstream_monthly_hydrology["results"]["risk1"],
            "rm2": downstream_monthly_hydrology["results"]["risk2"],
            "rm3": downstream_monthly_hydrology["results"]["risk3"],
            "meanAnnualDischarge": sum([float(monthly_discharge) for monthly_discharge in downstream_monthly_hydrology["results"]["mad_m3s"]]),
            "monthlyFlowSensitivities": downstream_monthly_hydrology["results"]["flow_sens"],
            "monthlyDischargePercentages": downstream_monthly_hydrology["results"]["pct_mad"],
            "waterLicenceMonthlyDisplay": downstream_monthly_hydrology["results"]["long_display"],
            "shortTermAllocationMonthlyDisplay": downstream_monthly_hydrology["results"]["short_display"]
        },
        "annualHydrology": annual_hydrology['results'] if annual_hydrology else [],
        "licenceImportDates": licence_import_dates
    }, 200
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise RuntimeError(f"Failed building watershed report due to:\n{tb}")
