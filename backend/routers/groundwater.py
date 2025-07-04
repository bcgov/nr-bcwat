from flask import Blueprint, current_app as app
from utils.general import generate_stations_as_features
from utils.groundwater import generate_groundwater_level_station_metrics, generate_groundwater_quality_station_metrics

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

    groundwater_level_station_metadata = app.db.get_station_by_type_and_id(type_id=2, station_id=id)
    raw_groundwater_level_station_metrics = app.db.get_groundwater_level_station_report_by_id(station_id=id)
    computed_groundwater_level_station_metrics = generate_groundwater_level_station_metrics(raw_groundwater_level_station_metrics)

    return {
        "name": groundwater_level_station_metadata["name"],
        "nid": groundwater_level_station_metadata["nid"],
        "net": groundwater_level_station_metadata["net"],
        "yr": groundwater_level_station_metadata["yr"],
        "ty": groundwater_level_station_metadata["ty"],
        "description": groundwater_level_station_metadata["description"],
        "licence_link": groundwater_level_station_metadata["licence_link"],
        "hydrograph": computed_groundwater_level_station_metrics["hydrograph"],
        "monthly_mean_flow": computed_groundwater_level_station_metrics["monthly_mean_flow"]
    }, 200

@groundwater.route('/quality/stations/<int:id>/report', methods=['GET'])
def get_groundwater_quality_station_report_by_id(id):
    """
        Computes Groundwater Quality Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    groundwater_quality_station_metadata = app.db.get_station_by_type_and_id(type_id=5, station_id=id)
    raw_groundwater_quality_station_metrics = app.db.get_groundwater_quality_station_report_by_id(station_id=id)
    computed_groundwater_quality_station_metrics = generate_groundwater_quality_station_metrics(raw_groundwater_quality_station_metrics)

    return {
        "name": groundwater_quality_station_metadata["name"],
        "nid": groundwater_quality_station_metadata["nid"],
        "net": groundwater_quality_station_metadata["net"],
        "yr": groundwater_quality_station_metadata["yr"],
        "ty": groundwater_quality_station_metadata["ty"],
        "description": groundwater_quality_station_metadata["description"],
        "licence_link": groundwater_quality_station_metadata["licence_link"],
        "sparkline": computed_groundwater_quality_station_metrics
    }, 200
