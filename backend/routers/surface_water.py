from flask import Blueprint, current_app as app

surface_water = Blueprint('surface_water', __name__)

@surface_water.route('/stations', methods=['GET'])
def get_surface_water_stations():

    response = app.db.get_surface_water_stations()

    return response, 200


@surface_water.route('/stations/<int:id>/report', methods=['GET'])
def get_surface_water_station_report_by_id(id):

    response = app.db.get_surface_water_station_report_by_id()

    return response, 200
