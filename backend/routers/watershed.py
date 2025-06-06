from flask import Blueprint, current_app as app

watershed = Blueprint('watershed', __name__)

@watershed.route('/reports', methods=['GET'])
def get_watershed_reports():

    response = app.db.get_watershed_reports()

    return response, 200

@watershed.route('/stations', methods=['GET'])
def get_watershed_stations():

    response = app.db.get_watershed_stations()

    return response, 200

