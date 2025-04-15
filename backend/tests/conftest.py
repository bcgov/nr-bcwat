import wsgi
import pytest

@pytest.fixture
def app():
    app = wsgi.app
    return app

@pytest.fixture()
def client(app):
    return app.test_client()
