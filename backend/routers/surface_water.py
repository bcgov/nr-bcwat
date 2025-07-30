from flask import Blueprint, current_app as app
from utils.surface_water import generate_surface_water_station_metrics

surface_water = Blueprint('surface_water', __name__)

@surface_water.route('/stations', methods=['GET'])
def get_surface_water_stations():
    """
        Returns all Stations within Surface Water Module
    """

    surface_water_features = app.db.get_stations_by_type(type_id=[4])

    # Prevent Undefined Error on FrontEnd
    if surface_water_features['geojson']['features'] is None:
        surface_water_features['geojson']['features'] = []

    return {
            "type": "FeatureCollection",
            "features": surface_water_features['geojson']['features']
            }, 200


@surface_water.route('/stations/<int:id>/report', methods=['GET'])
def get_surface_water_station_report_by_id(id):
    """
        Computes Surface Water Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    surface_water_station_metadata = app.db.get_station_by_type_and_id(type_id=[4], station_id=id)

    if not surface_water_station_metadata:
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

    raw_surface_water_station_metrics = app.db.get_surface_water_station_report_by_id(station_id=id)

    if not len(raw_surface_water_station_metrics):
        # Metrics Not Found for Station
        return {
            "name": surface_water_station_metadata["name"],
            "nid": surface_water_station_metadata["nid"],
            "net": surface_water_station_metadata["net"],
            "yr": surface_water_station_metadata["yr"],
            "ty": surface_water_station_metadata["ty"],
            "description": surface_water_station_metadata["description"],
            "licence_link": surface_water_station_metadata["licence_link"],
            "sparkline": {}
        }, 404

    try:
        (computed_surface_water_station_metrics, unique_params, sample_dates) = generate_surface_water_station_metrics(raw_surface_water_station_metrics)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Metrics for Surface Water Station: {surface_water_station_metadata['name']} (Id: {id})",
                "server_message": error,
                "status_code": 500
            })

    return {
        "name": surface_water_station_metadata["name"],
        "nid": surface_water_station_metadata["nid"],
        "net": surface_water_station_metadata["net"],
        "yr": surface_water_station_metadata["yr"],
        "ty": surface_water_station_metadata["ty"],
        "description": surface_water_station_metadata["description"],
        "licence_link": surface_water_station_metadata["licence_link"],
        "sparkline": computed_surface_water_station_metrics,
        "uniqueParams": unique_params,
        "sampleDates": sample_dates
    }, 200

@surface_water.route('/stations/<int:id>/station-statistics', methods=['GET'])
def get_surface_water_station_statistics(id):
    """
        Get Groundwater station statistics for the given station ID.
        These are the number of unique parameters and the number of days analysed.
    """
    groundwater_station_statistics = app.db.get_water_quality_station_statistics(station_id = id)

    return {
        "uniqueParams": groundwater_station_statistics['unique_params'],
        "sampleDates": groundwater_station_statistics['sample_dates']
    }
