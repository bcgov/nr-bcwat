from flask import Blueprint, Response, current_app as app
from utils.streamflow import (
    generate_streamflow_station_metrics,
    generate_flow_metrics
)
from utils.shared import (
    generate_station_csv
)
from constants import STREAMFLOW_VARIABLE_IDS

streamflow = Blueprint('streamflow', __name__)

@streamflow.route('/stations', methods=['GET'])
def get_streamflow_stations():
    """
        Returns all Stations within Streamflow Module
    """
    streamflow_features = app.db.get_streamflow_stations(**STREAMFLOW_VARIABLE_IDS)

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
            "monthlyMeanFlow": {},
            "stage": {},
            "flowDurationTool": {},
            "flowMetrics": {},
            "hasStationMetrics": False,
            "hasFlowMetrics": False,
            "meanAnnualFlow": None
        }, 400

    raw_streamflow_station_metrics = app.db.get_streamflow_station_report_by_id(station_id=id)
    raw_streamflow_flow_metrics = app.db.get_streamflow_station_flow_metrics_by_id(station_id=id)

    has_station_metrics = raw_streamflow_station_metrics is not None
    has_flow_metrics = raw_streamflow_flow_metrics is not None

    if not has_station_metrics and not has_flow_metrics:
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
            "monthlyMeanFlow": {},
            "stage": {},
            "flowDurationTool": {},
            "flowMetrics": {},
            "hasStationMetrics": has_station_metrics,
            "hasFlowMetrics": has_flow_metrics,
            "meanAnnualFlow": None
        }, 404

    if has_station_metrics:
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
            "monthlyMeanFlow": {},
            "stage": {},
            "flowDurationTool": {},
            "meanAnnualFlow": None
        }

    if has_flow_metrics:
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

    response =  {
        "name": streamflow_station_metadata["name"],
        "nid": streamflow_station_metadata["nid"],
        "net": streamflow_station_metadata["net"],
        "yr": streamflow_station_metadata["yr"],
        "ty": streamflow_station_metadata["ty"],
        "description": streamflow_station_metadata["description"],
        "licence_link": streamflow_station_metadata["licence_link"],
        "sevenDayFlow":  computed_streamflow_station_metrics['sevenDayFlow'],
        "monthlyMeanFlow":  computed_streamflow_station_metrics['monthlyMeanFlow'],
        "stage": computed_streamflow_station_metrics['stage'],
        "flowDurationTool": computed_streamflow_station_metrics['flowDurationTool'],
        "flowMetrics": computed_streamflow_flow_metrics,
        "hasStationMetrics": has_station_metrics,
        "hasFlowMetrics": has_flow_metrics,
        "meanAnnualFlow": computed_streamflow_station_metrics["meanAnnualFlow"]
    }

    return response, 200

@streamflow.route('/stations/<int:id>/csv', methods=['GET'])
def get_streamflow_station_csv_by_id(id):
    """
        Returns Simple CSV for Station ID containing raw data

        Path Parameters:
            id (int): Station ID.
    """

    streamflow_station_metadata = app.db.get_station_csv_metadata_by_type_and_id(type_id=[1], station_id=id)

    if not streamflow_station_metadata:
        # Metrics Not Found for Station
        return {
            "name": None,
            "nid": None,
            "net": None,
            "description": None,
            "licence_link": None
        }, 400

    raw_streamflow_station_metrics = app.db.get_streamflow_station_csv_by_id(station_id=id)

    if not len(raw_streamflow_station_metrics):
        # Metrics Not Found for Station
        # Unable to return CSV
        return {
            "name": streamflow_station_metadata["name"],
            "nid": streamflow_station_metadata["nid"],
            "net": streamflow_station_metadata["net"],
            "description": streamflow_station_metadata["description"],
            "licence_link": streamflow_station_metadata["licence_link"]
        }, 404

    streamflow_station_csv = generate_station_csv(station_metadata=streamflow_station_metadata, metrics=raw_streamflow_station_metrics)

    return Response(streamflow_station_csv, mimetype='text/csv'), 200
