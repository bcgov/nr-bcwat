from flask import Blueprint, current_app as app

climate = Blueprint('climate', __name__)

@climate.route('/reports', methods=['GET'])
def get_climate_reports():

    response = app.db.get_climate_reports()

    return response, 200

@climate.route('/stations', methods=['GET'])
def get_climate_stations():

    response = app.db.get_climate_stations()

    return response, 200

