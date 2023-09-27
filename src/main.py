from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.app_config")
    db = SQLAlchemy(app)
    
    return app