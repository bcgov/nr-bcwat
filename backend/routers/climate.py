from flask import Blueprint, current_app as app

climate = Blueprint('climate', __name__)

@climate.route('/stations', methods=['GET'])
def get_climate_stations():

    response = app.db.get_climate_stations()

    return response, 200

@climate.route('/stations/<int:id>/report', methods=['GET'])
def get_climate_station_report_by_id(id):

    response = app.db.get_climate_station_report_by_id()

    return response, 200
