from flask import Blueprint, current_app as app

climate = Blueprint('climate', __name__)

@climate.route('/stations', methods=['GET'])
def get_climate_stations():
    """
        Returns all Stations within Climate Module
    """

    response = app.db.get_climate_stations()

    return response, 200

@climate.route('/stations/<int:id>/report', methods=['GET'])
def get_climate_station_report_by_id(id):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_climate_station_report_by_id(id = id)

    return response, 200
