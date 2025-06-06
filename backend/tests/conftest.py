import os
import wsgi
import pytest
from mock_database import MockDatabase

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
