import os
import json
import tempfile
import shutil
import pytest
from app import create_app

@pytest.fixture
def app():
    # Create a temporary directory for DATA_PATH
    temp_dir = tempfile.mkdtemp()

    app = create_app()
    app.config['DATA_PATH'] = temp_dir  # Override path for testing
    yield app

    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def client(app):
    return app.test_client()

def test_app_creation(app):
    """Test that the Flask app is created and has the required attributes."""
    assert app is not None
    assert app.config['DATA_PATH']
    assert os.path.exists(app.config['DATA_PATH'])
    assert hasattr(app, 'load_json')
    assert hasattr(app, 'save_json')

def test_save_and_load_json(app):
    """Test saving and loading JSON data."""
    test_data = [{"id": 1, "name": "Test"}]

    # Save JSON
    app.save_json("test.json", test_data)

    # Check file exists
    file_path = os.path.join(app.config['DATA_PATH'], "test.json")
    assert os.path.exists(file_path)

    # Load JSON
    loaded_data = app.load_json("test.json")
    assert loaded_data == test_data

def test_load_json_file_not_exist(app):
    """Test loading JSON when file does not exist."""
    data = app.load_json("nonexistent.json")
    assert data == []
