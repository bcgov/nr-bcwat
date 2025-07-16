import os
import json
from constants import logger
from database import Database
from flask import Flask, jsonify
from flask_cors import CORS
from routers.climate import climate
from routers.groundwater import groundwater
from routers.streamflow import streamflow
from routers.surface_water import surface_water
from routers.watershed import watershed
from swagger_ui import flask_api_doc

def create_app():

    app = Flask(__name__)

    app.db = Database()

    environment = os.environ.get('FLASK_ENV', 'Unit_Test')
    # Allowed origins
    origins = None
    if (environment == 'development'):
        origins = "*"
    else:
        origins = os.environ.get('CLIENT_URL', 'nr-bcwat.unit-tests')
    CORS(app, resources={r"*": {"origins": origins}})


    @app.route('/health')
    def health_check():
        return 'Healthy', 200

    @app.route('/docs/swagger.json')
    def swagger_spec():
        with open('documentation/openapi.json') as f:
            return jsonify(json.load(f))

    flask_api_doc(
        app,
        config_path='/docs/swagger.json',
        url_prefix='/docs'
    )

    app.register_blueprint(climate, url_prefix='/climate')
    app.register_blueprint(groundwater, url_prefix='/groundwater')
    app.register_blueprint(streamflow, url_prefix='/streamflow')
    app.register_blueprint(surface_water, url_prefix='/surface-water')
    app.register_blueprint(watershed, url_prefix='/watershed')

    @app.errorhandler(Exception)
    def handle_error(error):
        message = "Internal Server Error"
        status_code = 500
        try:
            server_message = f" - ERROR - " + str(error)

        except Exception as e:
            server_message = " - ERROR - " + str(error)

        if len(error.args) > 0 and type(error.args[0]) is dict:
            if 'user_message' in error.args[0]:
                message = error.args[0]["user_message"]
            if 'status_code' in error.args[0]:
                status_code = error.args[0]['status_code']
            if 'server_message' in error.args[0]:
                try:
                    server_message = " - ERROR - " + error.args[0]['server_message']
                except Exception:
                    server_message = " - ERROR - " + str(error)

        logger.error(server_message)
        return { "message" : message }, status_code

    return app
