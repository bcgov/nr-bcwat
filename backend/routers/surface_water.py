from flask import Blueprint, current_app as app

surface_water = Blueprint('surface_water', __name__)

@surface_water.route('/stations', methods=['GET'])
def get_surface_water_stations():
    """
        Returns all Stations within Surface Water Module
    """

    response = app.db.get_surface_water_stations()

    return response, 200


@surface_water.route('/stations/<int:id>/report', methods=['GET'])
def get_surface_water_station_report_by_id(id):
    """
        Computes Surface Water Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_surface_water_station_report_by_id(id = id)

    return response, 200
