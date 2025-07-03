from flask import Blueprint, current_app as app
from utils.general import generate_stations_as_features

surface_water = Blueprint('surface_water', __name__)

@surface_water.route('/stations', methods=['GET'])
def get_surface_water_stations():
    """
        Returns all Stations within Surface Water Module
    """

    surface_water_stations = app.db.get_surface_water_stations()
    surface_water_features = generate_stations_as_features(surface_water_stations)
    return {
            "type": "FeatureCollection",
            "features": surface_water_features
            }, 200


@surface_water.route('/stations/<int:id>/report', methods=['GET'])
def get_surface_water_station_report_by_id(id):
    """
        Computes Surface Water Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_surface_water_station_report_by_id(station_id=id)

    return response, 200
