import os
import json
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

@pytest.fixture
def streamflow_input_fixture():
    path = os.path.join(os.path.dirname(__file__), 'fixtures/streamflow', 'fullStreamflow.json')
    with open(path, 'r') as f:
        return json.load(f)

@pytest.fixture
def total_runoff_output_fixture():
    path = os.path.join(os.path.dirname(__file__), 'fixtures/streamflow', 'totalRunoff.json')
    with open(path, 'r') as f:
        return json.load(f)

@pytest.fixture
def flow_exceedance_output_fixture():
    path = os.path.join(os.path.dirname(__file__), 'fixtures/streamflow', 'flowExceedance.json')
    with open(path, 'r') as f:
        return json.load(f)
