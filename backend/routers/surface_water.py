from flask import Blueprint, current_app as app
from utils.surface_water import generate_surface_water_station_metrics

surface_water = Blueprint('surface_water', __name__)

@surface_water.route('/stations', methods=['GET'])
def get_surface_water_stations():
    """
        Returns all Stations within Surface Water Module
    """

    surface_water_features = app.db.get_stations_by_type(type_id=4)

    return {
            "type": "featureCollection",
            "features": surface_water_features
            }, 200


@surface_water.route('/stations/<int:id>/report', methods=['GET'])
def get_surface_water_station_report_by_id(id):
    """
        Computes Surface Water Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    surface_water_station_metadata = app.db.get_station_by_type_and_id(type_id=4, station_id=id)
    raw_surface_water_station_metrics = app.db.get_surface_water_station_report_by_id(station_id=id)
    computed_surface_water_station_metrics = generate_surface_water_station_metrics(raw_surface_water_station_metrics)

    return {
        "name": surface_water_station_metadata["name"],
        "nid": surface_water_station_metadata["nid"],
        "net": surface_water_station_metadata["net"],
        "yr": surface_water_station_metadata["yr"],
        "ty": surface_water_station_metadata["ty"],
        "description": surface_water_station_metadata["description"],
        "licence_link": surface_water_station_metadata["licence_link"],
        "sparkline": computed_surface_water_station_metrics
    }, 200
