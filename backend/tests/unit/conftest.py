import os
import json
import wsgi
import pytest
from mock_database import MockDatabase
from unittest.mock import MagicMock

os.environ['FLASK_ENV'] = 'Unit_Test'
os.environ['CLIENT_URL'] = 'nr-bcwat.unit-tests'

@pytest.fixture
def app():
    app = wsgi.app
    app.db = MockDatabase()
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture
def mock_features_none(app):
    """
        Inject a fake db method that returns features=None into app context.
    """
    with app.app_context():
        app.db = MagicMock()
        app.db.get_stations_by_type.return_value = {
            "geojson": {
                "features": None
            }
        }
        yield app.db.get_stations_by_type
