import pandas as pd
import numpy as np
import pickle

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
    return data[distances <= radius]['restaurant_id'].tolist(), data[distances <= radius]['zone_id'].tolist()

def get_coords(latitude, longitude, radius, day, time, localeBusyness, restaurantBusyness):
    data = pd.read_csv("restaurants.csv")

    center_lat = latitude
    center_lon = longitude
    radius = radius
    restaurants_within_radius, zone = find_restaurants_within_radius(data, center_lat, center_lon, radius)

    model = pickle.load()
    busyness = model.predict()

    df = pd.DataFrame({ "zone": zone, "busyness": busyness})

    max_busyness = max(df['busyness'])
    min_busyness = min(df['busyness'])

    df['localeBusyness'] = df['busyness'].apply(lambda x: {
        "Quiet": 1 if x == min_busyness else 0,
        "Average": 1 if min_busyness < x < max_busyness else 0,
        "Busy": 1 if x == max_busyness else 0,
        "importance": localeBusyness["importance"]
    })

    df = df.sort_values(by=['localeBusyness'], ascending=False)

    if localeBusyness["importance"] == "Strict":
        df = df[df['localeBusyness'].notnull()]
    df = df.reset_index(drop=True)

    tags = pd.read_csv("Tags.csv")

    print(df)

    return (latitude, longitude)




