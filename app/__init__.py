# __init__.py

from flask import Flask
import json
import os
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    # Path to JSON data folder
    app.config['DATA_PATH'] = os.path.join(os.path.dirname(__file__), 'data')

    # Ensure data folder exists
    if not os.path.exists(app.config['DATA_PATH']):
        os.makedirs(app.config['DATA_PATH'])

    # Helper function to load JSON files
    def load_json(filename):
        file_path = os.path.join(app.config['DATA_PATH'], filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return []

    # Helper function to save JSON files
    def save_json(filename, data):
        file_path = os.path.join(app.config['DATA_PATH'], filename)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

    # Attach helper functions to app context
    app.load_json = load_json
    app.save_json = save_json

    app.register_blueprint(main)
    return app

