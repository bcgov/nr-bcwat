from flask import Blueprint, current_app as app
from utils.climate import generate_climate_station_metrics

climate = Blueprint('climate', __name__)

@climate.route('/stations', methods=['GET'])
def get_climate_stations():
    """
        Returns all Stations within Climate Module
    """

    climate_features = app.db.get_stations_by_type(type_id=3)

    return {
            "type": "FeatureCollection",
            "features": climate_features
            }, 200

@climate.route('/stations/<int:id>/report', methods=['GET'])
def get_climate_station_report_by_id(id):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    climate_station_metadata = app.db.get_station_by_type_and_id(type_id=3, station_id=id)
    raw_climate_station_metrics = app.db.get_climate_station_report_by_id(station_id=id)

    computed_climate_station_metrics = generate_climate_station_metrics(raw_climate_station_metrics)

    return {
        "name": climate_station_metadata["name"],
        "nid": climate_station_metadata["nid"],
        "net": climate_station_metadata["net"],
        "yr": climate_station_metadata["yr"],
        "ty": climate_station_metadata["ty"],
        "description": climate_station_metadata["description"],
        "licence_link": climate_station_metadata["licence_link"],
        "temperature": computed_climate_station_metrics["temperature"],
        "precipitation": computed_climate_station_metrics["precipitation"],
        "snow_on_ground_depth": computed_climate_station_metrics["snow_on_ground_depth"],
        "snow_water_equivalent": computed_climate_station_metrics["snow_water_equivalent"],
        "manual_snow_survey": computed_climate_station_metrics["manual_snow_survey"]
    }, 200
