from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


from config import config_dict
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
jwt = JWTManager()

def createApp():
    app = Flask(__name__)
    
    config_mode = os.getenv('FLASK_ENVIRONMENT', 'Development')
    app.config.from_object(config_dict[config_mode])

    db.init_app(app)

    bcrypt.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login_form'
    login_manager.login_message_category = 'info'

    jwt.init_app(app)

    from . import models

    from . import forms

    from .routes import routes

    app.register_blueprint(routes, url_prefix='/')

    createDatabase(app)

    return app

def createDatabase(app):
    with app.app_context():
        db.create_all()
