from flask import Flask
import mysql.connector
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_secret_key'

    app.config['DB_CONFIG'] = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'budget-planner'
    }

    app.register_blueprint(main)

    return app
