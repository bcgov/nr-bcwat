from flask import Blueprint, current_app as app
from utils.climate import generate_climate_stations_features

climate = Blueprint('climate', __name__)

@climate.route('/stations', methods=['GET'])
def get_climate_stations():
    """
        Returns all Stations within Climate Module
    """

    climate_stations = app.db.get_climate_stations()
    climate_features = generate_climate_stations_features(climate_stations)
    return {
            "type": "featureCollection",
            "features": climate_features
            }, 200

@climate.route('/stations/<int:id>/report', methods=['GET'])
def get_climate_station_report_by_id(id):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_climate_station_report_by_id(id = id)

    return response, 200
