from flask import Blueprint, request, current_app as app
from utils.general import generate_stations_as_features

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():
    """
        Returns all Stations within Streamflow Module
    """

    streamflow_stations = app.db.get_streamflow_stations()
    streamflow_features = generate_stations_as_features(streamflow_stations)
    return {
            "type": "featureCollection",
            "features": streamflow_features
            }, 200

@streamflow.route('/stations/<int:id>/report', methods=['GET'])
def get_streamflow_station_report_by_id(id):
    """
        Computes Streamflow Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    response = app.db.get_streamflow_station_report_by_id(station_id=id)

    return response, 200

@streamflow.route('/stations/<int:id>/report/flow-duration', methods=['GET'])
def get_streamflow_station_report_flow_duration_by_id(id):
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

    response = app.db.get_streamflow_station_report_flow_duration_by_id(station_id=id, start_year = start_year, end_year = end_year, month = month)
    # TODO - filter Lazy Frames by query params
    flow_duration = compute_all_metrics(response)

    return {"flowDuration": flow_duration}, 200
