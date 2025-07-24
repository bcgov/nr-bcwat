from flask import Blueprint, request, current_app as app

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

@watershed.route('/licence/search', methods=['GET'])
def get_watersheds_by_search_term():
    """
    Get Watershed by Search.

    Query Parameters:
        wls_id (string): water_licence_id
    """
    # Needed for ILIKE search
    wls_id = request.args.get('wls_id') + '%'

    if wls_id is None:
        return {
            "error": "Missing required query parameters 'wls_id'"
        }, 400

    nearest_watersheds = app.db.get_watershed_licences_by_search_term(water_licence_id=wls_id)

    if not len(nearest_watersheds):
        return {
            "results": []
        }, 404

    return {
        "results": nearest_watersheds
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

@watershed.route('/<int:id>/report', methods=['GET'])
def get_watershed_report_by_id(id):
    """
        Computes Watershed Metrics for Station ID.

        Path Parameters:
            id (int): Watershed ID.
    """

    watershed_metadata = app.db.get_watershed_report_by_id(watershed_feature_id=id)
    # print(json.dumps(watershed_metadata, indent=2))

    return watershed_metadata, 200
