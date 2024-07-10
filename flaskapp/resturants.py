import pandas as pd
import numpy as np
import pickle
from .models import Restaurant, Restaurant_Busyness, Tags, Zones
from .import db
from sqlalchemy.exc import SQLAlchemyError

def fetch_data(Table):
    try:
        station_data = db.session.query(Table).all()
        return station_data
    
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    km = 6371 * c 
    return km

def find_restaurants_within_radius(data, center_lat, center_lon, radius):
    distances = data.apply(lambda row: haversine(center_lon, center_lat, row['longitude'], row['latitude']), axis=1)
    return data[distances <= radius]['restaurant_id'].tolist()

def get_coords(latitude, longitude, radius, day, time, localeBusyness, restaurantBusyness):
    restaurant_data = pd.DataFrame([{
        "restaurant_id": restaurant.restaurant_id,
        "name": restaurant.name,
        "url": restaurant.url,
        "image_url": restaurant.image_url,
        "rating": restaurant.rating,
        "latitude": restaurant.latitude,
        "longitude": restaurant.longitude,
        "price": restaurant.price,
        "display_address": restaurant.display_address.replace('"', '').replace("'", ""),
        "zone_id": restaurant.zone_id
    } for restaurant in fetch_data(Restaurant)])

    restaurants_within_radius = find_restaurants_within_radius(restaurant_data, latitude, longitude, radius)

    # zone_id = db.Column(db.String(22), primary_key=True)
    # the_geom = db.Column(LONGTEXT)
    # zone_name = db.Column(db.String(255))
    # borough = db.Column(db.String(255))
    zones_data = pd.DataFrame([{
        "zone_id": zone.zone_id,
        "the_geom": zone.the_geom,
        "zone_name": zone.zone_name,
        "borough": zone.borough
    } for zone in fetch_data(Zones)])

    model = pickle.load()
    busyness = model.predict()

    zones_data["busyness"] = busyness

    max_busyness = max(zones_data['busyness'])
    min_busyness = min(zones_data['busyness'])

    zones_data['busyness_division'] = zones_data['busyness'].apply(lambda x: {
        "Quiet": 1 if x == min_busyness else 0,
        "Average": 1 if min_busyness < x < max_busyness else 0,
        "Busy": 1 if x == max_busyness else 0,
    })

    zones_data = zones_data.sort_values(by=['busyness_division', 'zone_name'], ascending=False)





