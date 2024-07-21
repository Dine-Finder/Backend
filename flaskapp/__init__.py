from flask import Flask, send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restful import Api
from flask_mail import Mail
import googlemaps

from config import config_dict
import os

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
jwt = JWTManager()
mail = Mail()

def createApp():
    app = Flask(__name__, static_folder='build', static_url_path='/')
    api = Api(app)
    CORS(app, origins="*")
    
    # Load configuration
    config_mode = os.getenv('FLASK_ENVIRONMENT', 'Development')
    app.config.from_object(config_dict[config_mode])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    # Initialize Flask extensions with the app instance
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login_form'
    login_manager.login_message_category = 'info'
    jwt.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail

    # Initialize Google Maps client and store it in app extensions
    app.extensions['gmaps'] = googlemaps.Client(key=app.config['REACT_APP_GOOGLE_MAPS_API_KEY'])

    # Import parts of our application
    from . import models
    from .routes import routes
    app.register_blueprint(routes, url_prefix='/')

    # Serve React frontend
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    createDatabase(app)

    return app

def createDatabase(app):
    """Create database tables within an application context if they don't already exist."""
    with app.app_context():
        db.create_all()
        print('Database created!')
