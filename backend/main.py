import os
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    environment = os.environ.get('FLASK_ENV', 'Unit_Test')
    # Allowed origins
    origins = None
    if (environment == 'development'):
        origins = "*"
    else:
        origins = os.environ.get('CLIENT_URL', 'nr-bcwat.unit-tests')
    CORS(app, resources={r"*": {"origins": origins}})

    @app.route('/')
    def hello_world():
        return 'Hello, World!', 200

    @app.route('/health')
    def health_check():
        return 'Healthy', 200

    return app
