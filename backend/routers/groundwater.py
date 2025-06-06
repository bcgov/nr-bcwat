from flask import Blueprint, current_app as app

groundwater = Blueprint('groundwater', __name__)

@groundwater.route('/level/reports', methods=['GET'])
def get_groundwater_level_reports():

    response = app.db.get_groundwater_level_reports()

    return response, 200

@groundwater.route('/level/stations', methods=['GET'])
def get_groundwater_level_stations():

    response = app.db.get_groundwater_level_stations()

    return response, 200

@groundwater.route('/quality/reports', methods=['GET'])
def get_groundwater_quality_reports():

    response = app.db.get_groundwater_quality_reports()

    return response, 200

@groundwater.route('/quality/stations', methods=['GET'])
def get_groundwater_quality_stations():

    response = app.db.get_groundwater_quality_stations()

    return response, 200
