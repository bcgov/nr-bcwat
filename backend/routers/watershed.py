from flask import Blueprint, request, current_app as app
import json

watershed = Blueprint('watershed', __name__)

@watershed.route('/', methods=['GET'])
def get_watershed_by_lat_lng():
    """
    Computes Nearest Watershed by Map Click.

    Query Parameters:
        lat (float): Latitude (required)
        lng (float): Longitude (required)
        range (float): Search Distance in meters (optional, defaults to 5000)
    """
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    search_range = request.args.get('range', default=5000, type=float)

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

    nearest_watershed = app.db.get_watershed_by_lat_lng(lat=lat, lng=lng, search_range=search_range)
    return {
        "lat": lat,
        "lng": lng,
        "range": search_range,
        "message": "Query successful"
    }

@watershed.route('/stations', methods=['GET'])
def get_watershed_stations():
    """
        Returns all Stations within Watershed Module
    """

    watershed_features = app.db.get_watershed_stations()

    return {
            "type": "FeatureCollection",
            "features": watershed_features['geojson']['features']
            }, 200

@watershed.route('/stations/<int:id>/report', methods=['GET'])
def get_watershed_station_report_by_id(id):
    """
        Computes Watershed Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    watershed_metadata = app.db.get_watershed_station_report_by_id(watershed_feature_id=id)
    # print(json.dumps(watershed_metadata, indent=2))

    return watershed_metadata, 200
