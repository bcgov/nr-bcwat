from flask import Blueprint, current_app as app

groundwater = Blueprint('groundwater', __name__)

@groundwater.route('/level/stations', methods=['GET'])
def get_groundwater_level_stations():

    response = app.db.get_groundwater_level_stations()

    return response, 200

@groundwater.route('/quality/stations', methods=['GET'])
def get_groundwater_quality_stations():

    response = app.db.get_groundwater_quality_stations()

    return response, 200

@groundwater.route('/level/station/<int:id>/report', methods=['GET'])
def get_groundwater_level_station_report_by_id(id):

    response = app.db.get_groundwater_level_station_report_by_id()

    return response, 200

@groundwater.route('/quality/station/<int:id>/report', methods=['GET'])
def get_groundwater_quality_station_report_by_id(id):

    response = app.db.get_groundwater_quality_station_report_by_id()

    return response, 200
