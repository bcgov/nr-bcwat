import os
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    environment = os.environ['FLASK_ENV']
    # Allowed origins
    origins = None
    if (environment == 'development'):
        origins = "*"
    else:
        origins = os.environ['CLIENT_URL']
    CORS(app, resources={r"*": {"origins": origins}})

    @app.route('/')
    def hello_world():
        return 'Hello, World!', 200

    @app.route('/health')
    def health_check():
        return 'Healthy', 200

    return app
