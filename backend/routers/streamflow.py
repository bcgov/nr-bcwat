from flask import Blueprint, request, current_app as app
from utils.streamflow import generate_streamflow_station_metrics, generate_flow_metrics
import json
from pathlib import Path

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():
    """
        Returns all Stations within Streamflow Module
    """

    streamflow_features = app.db.get_stations_by_type(type_id=[1])

    return {
            "type": "FeatureCollection",
            "features": streamflow_features['geojson']['features']
            }, 200

@streamflow.route('/stations/<int:id>/report', methods=['GET'])
def get_streamflow_station_report_by_id(id):
    """
        Computes Streamflow Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    streamflow_station_metadata = app.db.get_station_by_type_and_id(type_id=[1], station_id=id)

    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_by_id(station_id=id)
    raw_streamflow_flow_metrics = app.db.get_streamflow_station_flow_metrics_by_id(station_id=id)

    computed_streamflow_station_metrics = generate_streamflow_station_metrics(raw_streamflow_station_metrics)
    computed_streamflow_flow_metrics = generate_flow_metrics(raw_streamflow_flow_metrics)

    return {
        "name": streamflow_station_metadata["name"],
        "nid": streamflow_station_metadata["nid"],
        "net": streamflow_station_metadata["net"],
        "yr": streamflow_station_metadata["yr"],
        "ty": streamflow_station_metadata["ty"],
        "description": streamflow_station_metadata["description"],
        "licence_link": streamflow_station_metadata["licence_link"],
        "sevenDayFlow":  computed_streamflow_station_metrics['sevenDayFlow'],
        "flowDuration":  computed_streamflow_station_metrics['flowDuration'],
        "monthlyMeanFlow":  computed_streamflow_station_metrics['monthlyMeanFlow'],
        "flowMetrics": computed_streamflow_flow_metrics
    }, 200

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

    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_flow_duration_by_id(station_id=id, start_year = start_year, end_year = end_year, month = month)

    streamflow_station_metadata = app.db.get_station_by_type_and_id(type_id=[1], station_id=id)
    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_flow_duration_by_id(station_id=id, start_year = start_year, end_year = end_year, month = month)
    computed_streamflow_station_metrics = generate_streamflow_station_metrics(raw_streamflow_station_metrics)

    return {
        "name": streamflow_station_metadata["name"],
        "nid": streamflow_station_metadata["nid"],
        "net": streamflow_station_metadata["net"],
        "yr": streamflow_station_metadata["yr"],
        "ty": streamflow_station_metadata["ty"],
        "description": streamflow_station_metadata["description"],
        "licence_link": streamflow_station_metadata["licence_link"],
        "flowDuration": computed_streamflow_station_metrics
    }, 200
