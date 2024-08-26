import pytest
from flask import Flask
from flask.testing import FlaskClient
from routes import routes  # Import the routes Blueprint
import json

@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(routes)
    return app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

def test_root(client: FlaskClient):
    """Test the / endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'version' in data
    assert 'date' in data
    assert 'kubernetes' in data

def test_lookup_ipv4(client: FlaskClient):
    """Test the /v1/tools/lookup endpoint"""
    response = client.get('/v1/tools/lookup', query_string={'domain': 'google.com'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'domain' in data
    assert 'ipv4_addresses' in data

def test_validate_ipv4(client: FlaskClient):
    """Test the /v1/tools/validate endpoint"""
    response = client.get('/v1/tools/validate', query_string={'ip': '1.2.3.4'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'ip' in data
    assert 'valid' in data

def test_get_history(client: FlaskClient):
    """Test the /v1/history endpoint"""
    response = client.get('/v1/history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)  # Expect a list of history items

def test_metrics(client: FlaskClient):
    """Test the /metrics endpoint"""
    response = client.get('/metrics')
    assert response.status_code == 200

def test_health(client: FlaskClient):
    """Test the /health endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data

