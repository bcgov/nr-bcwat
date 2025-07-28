from flask import Blueprint, current_app as app
from utils.climate import generate_climate_station_metrics
from utils.shared import generate_yearly_metrics, write_json_response_to_fixture, write_db_response_to_fixture

climate = Blueprint('climate', __name__)

@climate.route('/stations', methods=['GET'])
def get_climate_stations():
    """
        Returns all Stations within Climate Module
    """

    climate_features = app.db.get_stations_by_type(type_id=[3,6])

    # Prevent Undefined Error on FrontEnd
    if climate_features['geojson']['features'] is None:
        climate_features['geojson']['features'] = []

    return {
            "type": "FeatureCollection",
            "features": climate_features['geojson']['features']
            }, 200

@climate.route('/stations/<int:id>/report', methods=['GET'])
def get_climate_station_report_by_id(id):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
    """

    climate_station_metadata = app.db.get_station_by_type_and_id(type_id=[3,6], station_id=id)

    if not climate_station_metadata:
        # Metrics Not Found for Station
        return {
            "name": None,
            "nid": None,
            "net": None,
            "yr": None,
            "ty": None,
            "description": None,
            "licence_link": None,
            "temperature": {},
            "precipitation": {},
            "snow_on_ground_depth": {},
            "snow_water_equivalent": {},
            "manual_snow_survey": {}
        }, 400

    raw_climate_station_metrics = app.db.get_climate_station_report_by_id(station_id=id)

    if not len(raw_climate_station_metrics):
        # Metrics Not Found for Station
        return {
            "name": climate_station_metadata["name"],
            "nid": climate_station_metadata["nid"],
            "net": climate_station_metadata["net"],
            "yr": climate_station_metadata["yr"],
            "ty": climate_station_metadata["ty"],
            "description": climate_station_metadata["description"],
            "licence_link": climate_station_metadata["licence_link"],
            "temperature": {},
            "precipitation": {},
            "snow_on_ground_depth": {},
            "snow_water_equivalent": {},
            "manual_snow_survey": {}
        }, 404

    try:
        computed_climate_station_metrics = generate_climate_station_metrics(raw_climate_station_metrics)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Metrics for Climate Station: {climate_station_metadata['name']} (Id: {id})",
                "server_message": error,
                "status_code": 500
            })

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

@climate.route('/stations/<int:id>/report/temperature/<int:year>', methods=['GET'])
def get_climate_station_temperature_by_id_and_year(id, year):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
            year (int): Year of interest.
    """

    raw_climate_station_metrics = app.db.get_climate_station_report_by_id(station_id=id)
    if not len(raw_climate_station_metrics):
        # Metrics Not Found for Station
        return {
            "temperature": {}
        }, 404

    try:
        temperature = generate_yearly_metrics(raw_climate_station_metrics, variable_ids=[6,8], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Temperature Metrics for Climate Station Id: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "temperature": temperature
    }, 200

@climate.route('/stations/<int:id>/report/precipitation/<int:year>', methods=['GET'])
def get_climate_station_precipitation_by_id_and_year(id, year):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
            year (int): Year of interest.
    """

    raw_climate_station_metrics = app.db.get_climate_station_report_by_id(station_id=id)
    if not len(raw_climate_station_metrics):
        # Metrics Not Found for Station
        return {
            "precipitation": {}
        }, 404

    try:
        precipitation = generate_yearly_metrics(raw_climate_station_metrics, variable_ids=[27], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Precipitation Metrics for Climate Station Id: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "precipitation": precipitation
    }, 200

@climate.route('/stations/<int:id>/report/snow-depth/<int:year>', methods=['GET'])
def get_climate_station_snow_on_ground_depth_by_id_and_year(id, year):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
            year (int): Year of interest.
    """

    raw_climate_station_metrics = app.db.get_climate_station_report_by_id(station_id=id)
    if not len(raw_climate_station_metrics):
        # Metrics Not Found for Station
        return {
            "snow_on_ground_depth": {}
        }, 404

    try:
        snow_on_ground_depth = generate_yearly_metrics(raw_climate_station_metrics, variable_ids=[5], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Snow Depth Metrics for Climate Station Id: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "snow_on_ground_depth": snow_on_ground_depth
    }, 200

@climate.route('/stations/<int:id>/report/snow-water-equivalent/<int:year>', methods=['GET'])
def get_climate_station_snow_water_equivalent_by_id_and_year(id, year):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
            year (int): Year of interest.
    """

    raw_climate_station_metrics = app.db.get_climate_station_report_by_id(station_id=id)
    if not len(raw_climate_station_metrics):
        # Metrics Not Found for Station
        return {
            "snow_water_equivalent": {}
        }, 404

    try:
        snow_water_equivalent = generate_yearly_metrics(raw_climate_station_metrics, variable_ids=[16], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Snow Water Equivalent Metrics for Climate Station Id: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "snow_water_equivalent": snow_water_equivalent
    }, 200

@climate.route('/stations/<int:id>/report/snow-survey/<int:year>', methods=['GET'])
def get_climate_station_manual_snow_survey_by_id_and_year(id, year):
    """
        Computes Climate Metrics for Station ID.

        Path Parameters:
            id (int): Station ID.
            year (int): Year of interest.
    """

    raw_climate_station_metrics = app.db.get_climate_station_report_by_id(station_id=id)
    if not len(raw_climate_station_metrics):
        # Metrics Not Found for Station
        return {
            "manual_snow_survey": {}
        }, 404

    try:
        manual_snow_survey = generate_yearly_metrics(raw_climate_station_metrics, variable_ids=[19], year=year)
    except Exception as error:
        raise Exception({
                "user_message": f"Error Calculating Yearly Manual Snow Survey Metrics for Climate Station Id: {id}",
                "server_message": error,
                "status_code": 500
            })

    return {
        "manual_snow_survey": manual_snow_survey
    }, 200
