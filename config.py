from datetime import timedelta
from dotenv import load_dotenv
import os

class Constants():
    # Secret key for the application (replace with a strong random string)
    SECRET_KEY = "12345!!er"

    # JWT Secret key for authentication (replace with a strong random string)
    JWT_SECRET_KEY = "12345!!er"

    # Database URI for development environment
    DEV_DATABASE_URI = "mysql://root:root@localhost/flaskapp"

    # Database URI for production environment
    PROD_DATABASE_URI = "your_production_database_uri"

def configure():
    load_dotenv()

configure()

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY')
    SECRET_KEY = Constants.SECRET_KEY
    CORS_HEADERS = 'Content-Type'
    # JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_SECRET_KEY = Constants.JWT_SECRET_KEY
    JWT_TOKEN_LOCATION = ['headers']


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI')
    SQLALCHEMY_DATABASE_URI = Constants.DEV_DATABASE_URI

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(seconds=3600)
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DATABASE_URI')

config_dict = {
    'Production': ProductionConfig,
    'Development': DevelopmentConfig
}


JCDecaux_dict = {
    'NAME' : "Dublin",
    'STATIONS' : "https://api.jcdecaux.com/vls/v1/stations",
    'API_KEY' : os.getenv('db_api')
}