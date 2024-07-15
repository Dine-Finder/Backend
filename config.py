from datetime import timedelta
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

configure()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    CORS_HEADERS = 'Content-Type'
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_TOKEN_LOCATION = ['headers']


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URI')

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
