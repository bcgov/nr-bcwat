from flask import Blueprint, current_app as app
from utils.streamflow import prepare_lazyframes, compute_flow_exceedance, compute_monthly_flow_statistics, compute_total_runoff

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():

    response = app.db.get_streamflow_stations()

    return response, 200

@streamflow.route('/stations/<int:id>/report', methods=['GET'])
def get_streamflow_station_report_by_id(id):

    response = app.db.get_streamflow_station_report_by_id()

    return response, 200

@streamflow.route('/stations/<int:id>/report/flow-duration', methods=['GET'])
def get_streamflow_station_report_low_duration_by_id(id):

    response = app.db.get_streamflow_station_report_flow_duration_by_id()

    fd_lf = prepare_lazyframes(response)

    total_runoff = compute_total_runoff(fd_lf).collect().to_dicts()

    monthly_summary = compute_monthly_flow_statistics(fd_lf).collect().to_dicts()

    flow_exceedance = compute_flow_exceedance(fd_lf).collect().to_dicts()

    return {
        'totalRunoff': total_runoff,
        'monthlyFlowStatistics': monthly_summary,
        'flowExceedance': flow_exceedance
    }, 200
