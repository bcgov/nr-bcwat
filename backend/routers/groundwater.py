from flask import Blueprint, current_app as app

groundwater = Blueprint('groundwater', __name__)

@groundwater.route('/level/stations', methods=['GET'])
def get_groundwater_level_stations():
    """
        Returns all Stations within Groundwater Level Module
    """

    response = app.db.get_groundwater_level_stations()

    return response, 200

@groundwater.route('/quality/stations', methods=['GET'])
def get_groundwater_quality_stations():
    """
        Returns all Stations within Groundwater Quality Module
    """

    response = app.db.get_groundwater_quality_stations()

    return response, 200

@groundwater.route('/level/stations/<int:id>/report', methods=['GET'])
def get_groundwater_level_station_report_by_id(id):
    """
        Computes Groundwater Level Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_groundwater_level_station_report_by_id(id = id)

    return response, 200

@groundwater.route('/quality/stations/<int:id>/report', methods=['GET'])
def get_groundwater_quality_station_report_by_id(id):
    """
        Computes Groundwater Quality Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_groundwater_quality_station_report_by_id(id = id)

    return response, 200
