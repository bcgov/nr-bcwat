from flask import Blueprint, current_app as app

watershed = Blueprint('watershed', __name__)

@watershed.route('/stations', methods=['GET'])
def get_watershed_stations():
    """
        Returns all Stations within Watershed Module
    """

    response = app.db.get_watershed_stations()

    return response, 200

@watershed.route('/stations/<int:id>/report', methods=['GET'])
def get_watershed_station_report_by_id(id):
    """
        Computes Watershed Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_watershed_station_report_by_id(id = id)

    return response, 200
