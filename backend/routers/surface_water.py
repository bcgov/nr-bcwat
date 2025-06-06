from flask import Blueprint, current_app as app

surface_water = Blueprint('surface_water', __name__)

@surface_water.route('/reports', methods=['GET'])
def get_surface_water_reports():

    response = app.db.get_surface_water_reports()

    return response, 200

@surface_water.route('/stations', methods=['GET'])
def get_surface_water_stations():

    response = app.db.get_surface_water_stations()

    return response, 200

