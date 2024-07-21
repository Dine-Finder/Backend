import os
import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import LONGTEXT

from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()

# class Restaurant(Base):
#     __tablename__ = 'restaurant'

#     restaurant_id = Column(String(22), primary_key=True)
#     name = Column(String(255))
#     url = Column(Text)
#     image_url = Column(Text)
#     rating = Column(Float)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)
#     price = Column(String(10))
#     display_address = Column(Text)
#     zone_id = Column(Integer)

# class Tags(Base):
#     __tablename__ = 'tags'

#     restaurant_id = Column(String(22), primary_key=True)
#     tags = Column(Text)

# class Zones(Base):
#     __tablename__ = 'zones'

#     zone_id = Column(Integer, primary_key=True)
#     the_geom = Column(LONGTEXT, nullable=False)
#     zone_name = Column(String(255))
#     borough = Column(String(255))

# class Busyness(Base):
#     __tablename__ = 'busyness'

#     restaurant_id = Column(String(22), primary_key=True)
#     Monday_populartimes = Column(String(255))
#     Tuesday_populartimes = Column(String(255))
#     Wednesday_populartimes = Column(String(255))
#     Thursday_populartimes = Column(String(255))
#     Friday_populartimes = Column(String(255))
#     Saturday_populartimes = Column(String(255))
#     Sunday_populartimes = Column(String(255))

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    image_file = Column(String(20), nullable=False, default='default.jpg')
    password = Column(String(60), nullable=False)
    is_confirmed = Column(Boolean, nullable=False, default=False)
    confirmed_on = Column(DateTime, nullable=True)


def load_data_into_table(file_path, model):
    df = pd.read_csv(file_path)

    try:
        df.to_sql(f'{model}', con=engine, if_exists='append', index=False)
        print("Data has been successfully saved to the database.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        session.close()

csv_files = {
    # 'restaurants': 'table_data/restaurant.csv',
    # 'tags': 'table_data/tags.csv',
    # 'zones': 'table_data/zones.csv',
    # 'restaurant_busyness': 'table_data/busyness.csv',
    'users': 'table_data/user.csv',
}

DEV_DATABASE_URI = os.getenv("DEV_DATABASE_URI")
engine = create_engine(DEV_DATABASE_URI)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# load_data_into_table(csv_files['restaurants'], "restaurant")
# load_data_into_table(csv_files['tags'], "tags")
# load_data_into_table(csv_files['zones'], "zones")
# load_data_into_table(csv_files['restaurant_busyness'], "busyness")
load_data_into_table(csv_files['users'], "user")


print("Data loaded successfully.")
