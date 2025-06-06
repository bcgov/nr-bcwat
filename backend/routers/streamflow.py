from flask import Blueprint, current_app as app

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/reports', methods=['GET'])
def get_streamflow_reports():

    response = app.db.get_streamflow_reports()

    return response, 200

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():

    response = app.db.get_streamflow_stations()

    return response, 200

