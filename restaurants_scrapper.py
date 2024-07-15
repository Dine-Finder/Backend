import json
import os
import requests
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurants'

    restaurant_id = Column(String(22), primary_key=True)
    name = Column(String(255))
    url = Column(Text)
    image_url = Column(Text)
    rating = Column(Float)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    price = Column(String(10))
    display_address = Column(Text)
    zone_id = Column(Integer)

api_url = 'https://api.yelp.com/v3/businesses/search'
key = os.getenv('BARRY_YELP')

headers = {
    'Authorization': 'Bearer %s' % key
}

data_loc = pd.read_csv("manhattan_grid_coordinates.csv")
LATITUDE = data_loc["latitude"].values
LONGITUDE = data_loc["longitude"].values

for i in range(490, len(LATITUDE)):
    parameters = {
        'term': 'Restaurant',
        'latitude': LATITUDE[i],
        'longitude': LONGITUDE[i],
        'radius': 500,
        'limit': 50
    }

    try:
        response = requests.get(api_url, headers=headers, params=parameters)
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from the API: {e}")
        exit()

    restaurants = data['businesses']
    restaurant_data = []
    for restaurant in restaurants:
        restaurant_data.append({
            'restaurant_id': restaurant.get('id'),
            'name': restaurant.get('name'),
            'url': restaurant.get('url'),
            'image_url': restaurant.get('image_url'),
            'rating': restaurant.get('rating'),
            'price': restaurant.get('price'),
            'latitude': restaurant.get('coordinates', {}).get('latitude'),
            'longitude': restaurant.get('coordinates', {}).get('longitude'),
            'display_address': '; '.join(restaurant.get('location', {}).get('display_address', []))
        })

    df = pd.DataFrame(restaurant_data)
    engine = create_engine(os.getenv('DEV_DATABASE_URI'))
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        df.to_sql('restaurants', con=engine, if_exists='append', index=False)
        print("Data has been successfully saved to the database.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        session.close()

