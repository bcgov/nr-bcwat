from flask import Blueprint, Response, current_app as app
from utils.groundwater import (
    generate_groundwater_level_station_metrics,
    generate_groundwater_quality_station_metrics
)
from utils.shared import (
    generate_yearly_metrics,
    generate_station_csv
)

groundwater = Blueprint('groundwater', __name__)

@groundwater.route('/level/stations', methods=['GET'])
def get_groundwater_level_stations():
    """
        Returns all Stations within Groundwater Level Module
    """

    groundwater_level_features = app.db.get_stations_by_type(type_id=[2])

    # Prevent Undefined Error on FrontEnd
    if groundwater_level_features['geojson']['features'] is None:
        groundwater_level_features['geojson']['features'] = []

    return {
            "type": "FeatureCollection",
            "features": groundwater_level_features['geojson']['features']
            }, 200

@groundwater.route('/quality/stations', methods=['GET'])
def get_groundwater_quality_stations():
    """
        Returns all Stations within Groundwater Quality Module
    """

    groundwater_quality_features = app.db.get_stations_by_type(type_id=[5])

    # Prevent Undefined Error on FrontEnd
    if groundwater_quality_features['geojson']['features'] is None:
        groundwater_quality_features['geojson']['features'] = []

    return {
            "type": "FeatureCollection",
            "features": groundwater_quality_features['geojson']['features']
            }, 200

@groundwater.route('/level/stations/<int:id>/report', methods=['GET'])
def get_groundwater_level_station_report_by_id(id):
    """
        Computes Groundwater Level Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    groundwater_level_station_metadata = app.db.get_station_by_type_and_id(type_id=[2], station_id=id)

    if not groundwater_level_station_metadata:
        # Metrics Not Found for Station
        return {
            "name": None,
            "nid": None,
            "net": None,
            "yr": None,
            "ty": None,
            "description": None,
            "licence_link": None,
            "hydrograph": {},
            "monthly_mean_flow": {}
        }, 400

    raw_groundwater_level_station_metrics = app.db.get_groundwater_level_station_report_by_id(station_id=id)

    if not len(raw_groundwater_level_station_metrics):
        # Metrics Not Found for Station
        return {
            "name": groundwater_level_station_metadata["name"],
            "nid": groundwater_level_station_metadata["nid"],
            "net": groundwater_level_station_metadata["net"],
            "yr": groundwater_level_station_metadata["yr"],
            "ty": groundwater_level_station_metadata["ty"],
            "description": groundwater_level_station_metadata["description"],
            "licence_link": groundwater_level_station_metadata["licence_link"],
            "hydrograph": {},
            "monthly_mean_flow": {}
        }, 404

    try:
        computed_groundwater_level_station_metrics = generate_groundwater_level_station_metrics(raw_groundwater_level_station_metrics)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Metrics for Groundwater Level Station: {groundwater_level_station_metadata['name']} (Id: {id})",
                "server_message": error,
                "status_code": 500
            })

    return {
        "name": groundwater_level_station_metadata["name"],
        "nid": groundwater_level_station_metadata["nid"],
        "net": groundwater_level_station_metadata["net"],
        "yr": groundwater_level_station_metadata["yr"],
        "ty": groundwater_level_station_metadata["ty"],
        "description": groundwater_level_station_metadata["description"],
        "licence_link": groundwater_level_station_metadata["licence_link"],
        "hydrograph": computed_groundwater_level_station_metrics["hydrograph"],
        "monthly_mean_flow": computed_groundwater_level_station_metrics["monthly_mean_flow"]
    }, 200


@groundwater.route('/level/stations/<int:id>/report/hydrograph/<int:year>', methods=['GET'])
def get_groundwater_level_station_report_by_id_and_year(id, year):
    """
        Computes Groundwater Level Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
            year (int): Year of interest.
    """

    raw_groundwater_level_station_metrics = app.db.get_groundwater_level_station_report_by_id(station_id=id)

    if not len(raw_groundwater_level_station_metrics):
        # Metrics Not Found for Station
        return {
            "hydrograph": {}
        }, 404

    try:
        hydrograph = generate_yearly_metrics(raw_groundwater_level_station_metrics, variable_ids=[3], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Metrics for Groundwater Level Station Id: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "hydrograph": hydrograph
    }, 200

@groundwater.route('/level/stations/<int:id>/csv', methods=['GET'])
def get_groundwater_level_station_csv_by_id(id):
    """
        Returns Simple CSV for Station ID containing raw data

        Path Parameters:
            id (int): Station ID.
    """

    groundwater_level_station_metadata = app.db.get_station_csv_metadata_by_type_and_id(type_id=[2], station_id=id)

    if not groundwater_level_station_metadata:
        # Metrics Not Found for Station
        return {
            "name": None,
            "nid": None,
            "net": None,
            "ty": None,
            "description": None,
            "licence_link": None
        }, 400

    raw_groundwater_level_station_metrics = app.db.get_groundwater_level_station_csv_by_id(station_id=id)

    if not len(raw_groundwater_level_station_metrics):
        # Metrics Not Found for Station
        # Unable to return CSV
        return {
            "name": groundwater_level_station_metadata["name"],
            "nid": groundwater_level_station_metadata["nid"],
            "net": groundwater_level_station_metadata["net"],
            "ty": groundwater_level_station_metadata["ty"],
            "description": groundwater_level_station_metadata["description"],
            "licence_link": groundwater_level_station_metadata["licence_link"]
        }, 404

    groundwater_level_station_csv = generate_station_csv(station_metadata=groundwater_level_station_metadata, metrics=raw_groundwater_level_station_metrics)

    return Response(groundwater_level_station_csv, mimetype='text/csv'), 200

@groundwater.route('/quality/stations/<int:id>/station-statistics', methods=['GET'])
def get_groundwater_station_statistics(id):
    """
        Get Groundwater station statistics for the given station ID.
        These are the number of unique parameters and the number of days analysed.
    """
    groundwater_station_statistics = app.db.get_water_quality_station_statistics(station_id = id)

    return {
        "uniqueParams": groundwater_station_statistics['unique_params'],
        "sampleDates": groundwater_station_statistics['sample_dates']
    }

@groundwater.route('/quality/stations/<int:id>/report', methods=['GET'])
def get_groundwater_quality_station_report_by_id(id):
    """
        Computes Groundwater Quality Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    groundwater_quality_station_metadata = app.db.get_station_by_type_and_id(type_id=[5], station_id=id)

    if not groundwater_quality_station_metadata:
        # Metrics Not Found for Station
        return {
            "name": None,
            "nid": None,
            "net": None,
            "yr": None,
            "ty": None,
            "description": None,
            "licence_link": None,
            "sparkline": {}
        }, 400

    raw_groundwater_quality_station_metrics = app.db.get_groundwater_quality_station_report_by_id(station_id=id)

    if not len(raw_groundwater_quality_station_metrics):
        # Metrics Not Found for Station
        return {
            "name": groundwater_quality_station_metadata["name"],
            "nid": groundwater_quality_station_metadata["nid"],
            "net": groundwater_quality_station_metadata["net"],
            "yr": groundwater_quality_station_metadata["yr"],
            "ty": groundwater_quality_station_metadata["ty"],
            "description": groundwater_quality_station_metadata["description"],
            "licence_link": groundwater_quality_station_metadata["licence_link"],
            "sparkline": {},
            "uniqueParams": 0,
            "sampleDates": 0
        }, 404

    try:
        (computed_groundwater_quality_station_metrics, unique_params, sample_dates)  = generate_groundwater_quality_station_metrics(raw_groundwater_quality_station_metrics)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Metrics for Groundwater Quality Station: {groundwater_quality_station_metadata['name']} (Id: {id})",
                "server_message": error,
                "status_code": 500
            })

    return {
        "name": groundwater_quality_station_metadata["name"],
        "nid": groundwater_quality_station_metadata["nid"],
        "net": groundwater_quality_station_metadata["net"],
        "yr": groundwater_quality_station_metadata["yr"],
        "ty": groundwater_quality_station_metadata["ty"],
        "description": groundwater_quality_station_metadata["description"],
        "licence_link": groundwater_quality_station_metadata["licence_link"],
        "sparkline": computed_groundwater_quality_station_metrics,
        "uniqueParams": unique_params,
        "sampleDates": sample_dates
    }, 200
