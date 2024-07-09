import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from tqdm import tqdm
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

database_uri = os.getenv("DEV_DATABASE_URI")
engine = create_engine(database_uri)

Session = sessionmaker(bind=engine)
session = Session()

from sqlalchemy import Table, MetaData

metadata = MetaData()
restaurants_table = Table('restaurants', metadata, autoload_with=engine)

query = restaurants_table.select().offset(5754).limit(7672 - 5754)
result = session.execute(query)

restaurant_ids = [row['restaurant_id'] for row in result]
restaurant_urls = [row['url'] for row in result]

def fetch_reviews_and_ratings(restaurant_url, num_reviews=10):
    try:
        response = requests.get(restaurant_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        reviews = soup.find_all('span', {'class': 'raw__09f24__T4Ezm', 'lang': 'en'}, limit=num_reviews)
        review_texts = [review.text.strip() for review in reviews]

        return review_texts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching restaurant page: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

pbar = tqdm(total=len(restaurant_urls), desc='Progress', unit='restaurants')

all_reviews = {}

for restaurant_url, restaurant_id in zip(restaurant_urls, restaurant_ids):
    reviews = fetch_reviews_and_ratings(restaurant_url)

    all_reviews[restaurant_id] = {
        "reviews": reviews,
    }

    pbar.update(1)

pbar.close()

with open("scraped_reviews.json", "w") as f:
    json.dump(all_reviews, f, indent=4)

print("Scraping completed and reviews saved to scraped_reviews.json")