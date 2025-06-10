from flask import Blueprint, request, current_app as app
from utils.streamflow import prepare_lazyframes, compute_flow_exceedance, compute_monthly_flow_statistics, compute_total_runoff

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():
    """
        Returns all Stations within Streamflow Module
    """

    response = app.db.get_streamflow_stations()

    return response, 200

@streamflow.route('/stations/<int:id>/report', methods=['GET'])
def get_streamflow_station_report_by_id(id):
    """
        Computes Streamflow Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_streamflow_station_report_by_id(id = id)

    return response, 200

@streamflow.route('/stations/<int:id>/report/flow-duration', methods=['GET'])
def get_streamflow_station_report_low_duration_by_id(id):
    """
        Computes Flow Duration Metrics for Station ID based on the provided date range.

        Path Parameters:
            id (int): Station ID.

        Query Parameters:
            start-year (int, optional): Start Year of Interest.
            end-year (int, optional): End Year of Interest.
            month (str, optional): Specific Month of Interest.
    """

    start_year = request.args.get('start-year')
    end_year = request.args.get('end-year')
    month = request.args.get('month')
    # TODO - fetch from DB based upon specific year range, month

    response = app.db.get_streamflow_station_report_flow_duration_by_id(id = id, start_year = start_year, end_year = end_year, month = month)

    fd_lf = prepare_lazyframes(response)

    total_runoff = compute_total_runoff(fd_lf).collect().to_dicts()

    monthly_summary = compute_monthly_flow_statistics(fd_lf).collect().to_dicts()

    flow_exceedance = compute_flow_exceedance(fd_lf).collect().to_dicts()

    return {
        'totalRunoff': total_runoff,
        'monthlyFlowStatistics': monthly_summary,
        'flowExceedance': flow_exceedance
    }, 200
