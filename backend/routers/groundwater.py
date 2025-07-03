from flask import Blueprint, current_app as app
from utils.general import generate_stations_as_features

groundwater = Blueprint('groundwater', __name__)

@groundwater.route('/level/stations', methods=['GET'])
def get_groundwater_level_stations():
    """
        Returns all Stations within Groundwater Level Module
    """

    groundwater_level_stations = app.db.get_stations_by_type(type_id=2)
    groundwater_level_features = generate_stations_as_features(groundwater_level_stations)
    return {
            "type": "featureCollection",
            "features": groundwater_level_features
            }, 200

@groundwater.route('/quality/stations', methods=['GET'])
def get_groundwater_quality_stations():
    """
        Returns all Stations within Groundwater Quality Module
    """

    groundwater_quality_stations = app.db.get_stations_by_type(type_id=5)
    groundwater_quality_features = generate_stations_as_features(groundwater_quality_stations)
    return {
            "type": "featureCollection",
            "features": groundwater_quality_features
            }, 200

@groundwater.route('/level/stations/<int:id>/report', methods=['GET'])
def get_groundwater_level_station_report_by_id(id):
    """
        Computes Groundwater Level Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_groundwater_level_station_report_by_id(station_id=id)

    return response, 200

@groundwater.route('/quality/stations/<int:id>/report', methods=['GET'])
def get_groundwater_quality_station_report_by_id(id):
    """
        Computes Groundwater Quality Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_groundwater_quality_station_report_by_id(station_id=id)

    return response, 200
