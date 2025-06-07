from flask import Blueprint, current_app as app

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():

    response = app.db.get_streamflow_stations()

    return response, 200

@streamflow.route('/station/<int:id>/report', methods=['GET'])
def get_streamflow_station_report_by_id(id):

    response = app.db.get_streamflow_station_report_by_id()

    return response, 200
