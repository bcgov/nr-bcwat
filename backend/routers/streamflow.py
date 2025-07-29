from flask import Blueprint, request, current_app as app
from utils.streamflow import (
    generate_streamflow_station_metrics,
    generate_flow_metrics,
    generate_filtered_streamflow_station_metrics
)
from utils.shared import generate_yearly_metrics
import json
from pathlib import Path

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():
    """
        Returns all Stations within Streamflow Module
    """

    streamflow_features = app.db.get_stations_by_type(type_id=[1])

    # Prevent Undefined Error on FrontEnd
    if streamflow_features['geojson']['features'] is None:
        streamflow_features['geojson']['features'] = []

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

    if not streamflow_station_metadata:
        # Metrics Not Found for Station
        return {
            "name": None,
            "nid": None,
            "net": None,
            "yr": None,
            "ty": None,
            "description": None,
            "licence_link": None,
            "sevenDayFlow": {},
            "flowDuration": {},
            "monthlyMeanFlow": {},
            "stage": {},
            "flowMetrics": {},
            "hasStationMetrics": hasStationMetrics,
            "hasFlowMetrics": hasFlowMetrics
        }, 400

    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_by_id(station_id=id)
    raw_streamflow_flow_metrics = app.db.get_streamflow_station_flow_metrics_by_id(station_id=id)

    hasStationMetrics = raw_streamflow_station_metrics is not None
    hasFlowMetrics = raw_streamflow_flow_metrics is not None

    if not hasStationMetrics and not hasFlowMetrics:
        # Metrics Not Found for Station
        return {
            "name": streamflow_station_metadata["name"],
            "nid": streamflow_station_metadata["nid"],
            "net": streamflow_station_metadata["net"],
            "yr": streamflow_station_metadata["yr"],
            "ty": streamflow_station_metadata["ty"],
            "description": streamflow_station_metadata["description"],
            "licence_link": streamflow_station_metadata["licence_link"],
            "sevenDayFlow": {},
            "flowDuration": {},
            "monthlyMeanFlow": {},
            "stage": {},
            "flowMetrics": {},
            "hasStationMetrics": hasStationMetrics,
            "hasFlowMetrics": hasFlowMetrics
        }, 404

    if hasStationMetrics:
        try:
            computed_streamflow_station_metrics = generate_streamflow_station_metrics(raw_streamflow_station_metrics)
        except Exception as error:
            raise Exception({
                    "user_message": f"Error Calculating Streamflow Metrics for Streamflow Station: {streamflow_station_metadata['name']} (Id: {id})",
                    "server_message": error,
                    "status_code": 500
                })
    else:
        computed_streamflow_station_metrics = {
            "sevenDayFlow": {},
            "flowDuration": {},
            "monthlyMeanFlow": {},
            "stage": {}
        }

    if hasFlowMetrics:
        try:
            computed_streamflow_flow_metrics = generate_flow_metrics(raw_streamflow_flow_metrics)
        except Exception as error:
            raise Exception({
                    "user_message": f"Error Calculating Flow Metrics for Streamflow Station: {streamflow_station_metadata['name']} (Id: {id})",
                    "server_message": error,
                    "status_code": 500
                })
    else:
        computed_streamflow_flow_metrics = []


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
        "stage": computed_streamflow_station_metrics['stage'],
        "flowDurationTool": computed_streamflow_station_metrics['flowDurationTool'],
        "flowMetrics": computed_streamflow_flow_metrics,
        "hasStationMetrics": hasStationMetrics,
        "hasFlowMetrics": hasFlowMetrics
    }, 200

@streamflow.route('/stations/<int:id>/report/seven-day-flow/<int:year>', methods=['GET'])
def get_streamflow_station_seven_day_flow_by_id_and_year(id, year):
    """
        Computes Streamflow Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_by_id(station_id=id)

    if not len(raw_streamflow_station_metrics):
        # Metrics Not Found for Station
        return {
            "sevenDayFlow": {}
        }, 404

    try:
        sevenDayFlow = generate_yearly_metrics(raw_streamflow_station_metrics, variable_ids=[1], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Seven Day Flow for Streamflow StationId: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "sevenDayFlow": sevenDayFlow
    }, 200

@streamflow.route('/stations/<int:id>/report/stage/<int:year>', methods=['GET'])
def get_streamflow_station_stage_by_id_and_year(id, year):
    """
        Computes Streamflow Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_by_id(station_id=id)

    if not len(raw_streamflow_station_metrics):
        # Metrics Not Found for Station
        return {
            "stage": {}
        }, 404

    try:
        stage = generate_yearly_metrics(raw_streamflow_station_metrics, variable_ids=[2], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Stage for Streamflow StationId: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "stage": stage
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

    start_year = int(start_year) if start_year is not None else None
    end_year = int(end_year) if end_year is not None else None
    month = int(month) if month is not None else None

    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_by_id(station_id=id)

    if not len(raw_streamflow_station_metrics):
        # Metrics Not Found for Station
        return {
            "flowDuration": {}
        }, 404
    computed_streamflow_station_metrics = generate_filtered_streamflow_station_metrics(raw_streamflow_station_metrics, start_year=start_year, end_year=end_year, month=month)

    return {
        "flowDuration": computed_streamflow_station_metrics
    }, 200
