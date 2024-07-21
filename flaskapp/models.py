import datetime
import json

from pyttsx3 import engine
from sqlalchemy import text, Text
from sqlalchemy.dialects.mysql import LONGTEXT

from flaskapp import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.id},{self.username}, {self.email}, {self.image_file}, {self.image_file}>'


class Restaurant(db.Model):
    restaurant_id = db.Column(db.String(22), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text)
    image_url = db.Column(db.Text)
    rating = db.Column(db.Float)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    price = db.Column(db.String(10))
    display_address = db.Column(db.Text)
    zone_id = db.Column(db.Integer)

    def __repr__(self):
        return f'<Restaurant {self.restaurant_id}, {self.name}, {self.rating}, {self.latitude}, {self.longitude}, {self.price}>'

class Zones(db.Model):
    zone_id = db.Column(db.Integer, primary_key=True)
    the_geom = db.Column(LONGTEXT)
    zone_name = db.Column(db.String(255))
    borough = db.Column(db.String(255))

    def __repr__(self):
        return f'<Zones {self.zone_id}, {self.zone_name}, {self.borough}>'
    
class Tags(db.Model):
    restaurant_id = db.Column(db.String(22), primary_key=True)
    tags = db.Column(db.Text)

class Busyness(db.Model):
    restaurant_id = db.Column(db.String(22), primary_key=True)
    Monday_populartimes = db.Column(db.String(255))
    Tuesday_populartimes = db.Column(db.String(255))
    Wednesday_populartimes = db.Column(db.String(255))
    Thursday_populartimes = db.Column(db.String(255))
    Friday_populartimes = db.Column(db.String(255))
    Saturday_populartimes = db.Column(db.String(255))
    Sunday_populartimes = db.Column(db.String(255))