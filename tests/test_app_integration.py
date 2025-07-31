import os
import json
import tempfile
import pytest
from app import create_app

@pytest.fixture
def client():
    """Create a test client with an isolated temporary data directory."""
    temp_dir = tempfile.TemporaryDirectory()
    app = create_app()

    # Override the DATA_PATH to use a temp directory for tests
    app.config['DATA_PATH'] = temp_dir.name
    app.config['TESTING'] = True

    # Ensure temporary data directory exists
    os.makedirs(app.config['DATA_PATH'], exist_ok=True)

    with app.test_client() as client:
        yield client

    temp_dir.cleanup()


def test_app_initialization(client):
    """Test that the app initializes correctly and the index route redirects to login."""
    response = client.get('/')
    assert response.status_code == 302  # Redirect to login
    assert '/login' in response.location


def test_data_folder_created(client):
    """Ensure that DATA_PATH directory is created."""
    assert os.path.exists(client.application.config['DATA_PATH'])


def test_json_helpers(client):
    """Test load_json and save_json helper functions."""
    app = client.application
    test_file = 'test_data.json'
    test_data = [{'id': 1, 'name': 'Sample'}]

    # Save JSON using app.save_json
    app.save_json(test_file, test_data)

    file_path = os.path.join(app.config['DATA_PATH'], test_file)
    assert os.path.exists(file_path)

    # Load JSON using app.load_json
    loaded_data = app.load_json(test_file)
    assert loaded_data == test_data


def test_blueprint_registered(client):
    """Ensure that the main blueprint is registered."""
    routes = [rule.endpoint for rule in client.application.url_map.iter_rules()]
    assert 'main.index' in routes  # The index route should exist


def test_login_page_renders(client):
    """Test that login page renders successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<form' in response.data  # Check that it renders a login form
