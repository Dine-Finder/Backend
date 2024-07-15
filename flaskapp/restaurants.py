import json
import pandas as pd
import numpy as np
import pickle
import gzip
from .models import Restaurant, Busyness, Tags, Zones
from .import db
from sqlalchemy.exc import SQLAlchemyError

def fetch_data(Table):
    try:
        return db.session.query(Table).all()
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def compute_distance(data, center_lat, center_lon, radius):
    """Compute and return restaurants within the given radius."""
    distances = data.apply(lambda row: haversine(center_lon, center_lat, row['longitude'], row['latitude']), axis=1)
    return data[distances <= radius]

def haversine(lon1, lat1, lon2, lat2):
    """Calculate the great circle distance between two points on the earth."""
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    km = 6371 * c 
    return km

def filter_by_zone(data, zone_ids):
    """Filter data based on zone IDs."""
    return data[data['zone_id'].isin(zone_ids)]

def filter_by_time(filtered_restaurants, day, hour):
    """Filter restaurants based on a specified day and time."""
    number_to_day_mapping = {
        0: 'sunday',
        1: 'monday',
        2: 'tuesday',
        3: 'wednesday',
        4: 'thursday',
        5: 'friday',
        6: 'saturday'
    }
    selected = []
    for i in range(len(filtered_restaurants)):
        day_column = f"{number_to_day_mapping[day]}_populartimes"
        popularity_times = json.loads(filtered_restaurants.loc[i, day_column]) if filtered_restaurants.loc[i, day_column] else [0]*24
        selected.append(popularity_times[hour] if hour < len(popularity_times) else 0)
    filtered_restaurants["restaurant_busyness"] = selected
    return filtered_restaurants

def merge_additional_data(filtered_restaurants):
    """Merge additional data like tags into the restaurant data."""
    restaurant_ids = filtered_restaurants['restaurant_id'].tolist()
    try:
        restaurant_tags_data = db.session.query(Tags).filter(Tags.restaurant_id.in_(restaurant_ids)).all()
        tag_data = pd.DataFrame([{"restaurant_id": rb.restaurant_id, "tags": rb.tags} for rb in restaurant_tags_data])
        filtered_restaurants = pd.merge(filtered_restaurants, tag_data, on="restaurant_id", how="left")
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
    return filtered_restaurants

def select_filtered(column, busyness, df):
    max_ = max(df[column])
    min_ = min(df[column])

    df['quiet'] = df[column].apply(lambda x: 1 if x == min_ else 0)
    df['average'] = df[column].apply(lambda x: 1 if min_ < x < max_ else 0)
    df['busy'] = df[column].apply(lambda x: 1 if x == max_ else 0)

    selected_local = {key for key, value in busyness.items() if value == 1 and key in {"Quiet", "Average", "Busy"}}

    if busyness.get("importance") and busyness.get("importance").lower() == "required":
        df = df[df[selected_local].any(axis=1)]

    return df

def predict_busyness(time, day, df):
    with gzip.open('model/model.pkl.gz', 'rb') as handle:
        model = pickle.load(handle)
    
    input_df = pd.DataFrame()
    input_df["hour"] = [time] * len(df)
    input_df["minute"] = [30] * len(df)
    input_df["weekday"] = [day] * len(df)
    input_df["LocationID"] = df["zone_id"].values

    output = model.predict(input_df)
    output[output < 0] = 1
    output *= 10

    return output

def get_busyness(row):
    if row['quiet'] == 1:
        return 'quiet'
    elif row['average'] == 1:
        return 'average'
    elif row['busy'] == 1:
        return 'busy'
    return None


def get_filters(latitude, longitude, radius, day, time, localeBusyness, restaurantBusyness):
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
    restaurant_data = compute_distance(restaurant_data, latitude, longitude, radius)
    zones = set(restaurant_data["zone_id"])

    zones_data = pd.DataFrame([{
        "zone_id": zone.zone_id,
        "the_geom": zone.the_geom,
        "zone_name": zone.zone_name,
        "borough": zone.borough
    } for zone in fetch_data(Zones) if zone.zone_id in zones])

    if not zones:
        return pd.DataFrame()
    
    busyness = predict_busyness(time, day, zones_data)
    zones_data["zone_busyness"] = busyness
    zones_data = select_filtered("zone_busyness", localeBusyness, zones_data)

    restaurant_data = filter_by_zone(restaurant_data, set(zones_data['zone_id']))
    restaurant_ids = set(restaurant_data['restaurant_id'].tolist())

    if not restaurant_ids:
        return pd.DataFrame()

    try:
        restaurant_busyness_data = db.session.query(Busyness).filter(Busyness.restaurant_id.in_(restaurant_ids)).all()
        busyness_data = pd.DataFrame([{
            "restaurant_id": rb.restaurant_id,
            "monday_populartimes": rb.Monday_populartimes,
            "tuesday_populartimes": rb.Tuesday_populartimes,
            "wednesday_populartimes": rb.Wednesday_populartimes,
            "thursday_populartimes": rb.Thursday_populartimes,
            "friday_populartimes": rb.Friday_populartimes,
            "saturday_populartimes": rb.Saturday_populartimes,
            "sunday_populartimes": rb.Sunday_populartimes,
        } for rb in restaurant_busyness_data])
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
        busyness_data = pd.DataFrame()

    restaurant_data = pd.merge(restaurant_data, busyness_data, on="restaurant_id", how="left")

    zones_data['zone_busyness_string'] = zones_data.apply(get_busyness, axis=1)
    zones_data.drop(['quiet', 'average', 'busy', 'the_geom'], axis=1, inplace=True)

    restaurant_data = pd.merge(restaurant_data, zones_data, on="zone_id", how="left")
    restaurant_data = filter_by_time(restaurant_data, day, time)

    restaurant_data = select_filtered("restaurant_busyness", restaurantBusyness, restaurant_data)
    restaurant_data['restaurant_busyness_string'] = restaurant_data.apply(get_busyness, axis=1)
    restaurant_data.drop(['quiet', 'average', 'busy'], axis=1, inplace=True)

    try:
        restaurant_tags_data = db.session.query(Tags).all()
    except SQLAlchemyError as e:
        print(f"SQLAlchemy Error: {e}")
    tag_data = pd.DataFrame([{"restaurant_id": rb.restaurant_id, "tags": rb.tags} for rb in restaurant_tags_data])
    if tag_data.empty:
        return pd.DataFrame()
    restaurant_data = pd.merge(restaurant_data, tag_data, on="restaurant_id", how="left")
    if len(restaurant_data) > 50:
        return restaurant_data
    return restaurant_data
