from flask import Blueprint, current_app as app
from utils.general import generate_stations_as_features
from utils.climate import generate_station_metrics

climate = Blueprint('climate', __name__)

@climate.route('/stations', methods=['GET'])
def get_climate_stations():
    """
        Returns all Stations within Climate Module
    """

    climate_stations = app.db.get_climate_stations()
    climate_features = generate_stations_as_features(climate_stations)
    return {
            "type": "FeatureCollection",
            "features": climate_features
            }, 200

@climate.route('/stations/<int:id>/report', methods=['GET'])
def get_climate_station_report_by_id(id):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    raw_station_metrics = app.db.get_climate_station_report_by_id(station_id = id)
    computed_station_metrics = generate_station_metrics(raw_station_metrics)

    return computed_station_metrics, 200
