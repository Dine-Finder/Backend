import os
import datetime
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.mysql import LONGTEXT

from dotenv import load_dotenv
load_dotenv()

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurant'

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

class Tags(Base):
    __tablename__ = 'tags'

    restaurant_id = Column(String(22), primary_key=True)
    tags = Column(Text)

class Zones(Base):
    __tablename__ = 'zones'

    zone_id = Column(Integer, primary_key=True)
    the_geom = Column(LONGTEXT, nullable=False)
    zone_name = Column(String(255))
    borough = Column(String(255))

class Busyness(Base):
    __tablename__ = 'busyness'

    restaurant_id = Column(String(22), primary_key=True)
    Monday_populartimes = Column(String(255))
    Tuesday_populartimes = Column(String(255))
    Wednesday_populartimes = Column(String(255))
    Thursday_populartimes = Column(String(255))
    Friday_populartimes = Column(String(255))
    Saturday_populartimes = Column(String(255))
    Sunday_populartimes = Column(String(255))

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120))
    image_file = Column(String(20), nullable=False, default='default.jpg')
    password = Column(String(60), nullable=False)
    posts = relationship('Post', backref='Author', lazy=True)
    role = relationship('Role', secondary='user_role', back_populates='user')

class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    content = Column(Text, nullable=False)
    date_posted = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)
    user = relationship('User', secondary='user_role', back_populates='role')

user_role = Table(
    'user_role', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)

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
    'restaurants': 'table_data/restaurant.csv',
    'tags': 'table_data/tags.csv',
    'zones': 'table_data/zones.csv',
    'restaurant_busyness': 'table_data/busyness.csv',
    'users': 'table_data/user.csv',
    'posts': 'table_data/post.csv',
    'roles': 'table_data/role.csv',
    'user_role': 'table_data/user_role.csv'
}

DEV_DATABASE_URI = os.getenv("DEV_DATABASE_URI")
engine = create_engine(DEV_DATABASE_URI)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

load_data_into_table(csv_files['restaurants'], "restaurant")
load_data_into_table(csv_files['tags'], "tags")
load_data_into_table(csv_files['zones'], "zones")
load_data_into_table(csv_files['restaurant_busyness'], "busyness")
load_data_into_table(csv_files['users'], "user")
load_data_into_table(csv_files['posts'], "post")
load_data_into_table(csv_files['roles'], "role")

df_user_role = pd.read_csv(csv_files['user_role'])
for index, row in df_user_role.iterrows():
    user_id = row['user_id']
    role_id = row['role_id']
    user = session.query(User).filter_by(id=user_id).first()
    role = session.query(Role).filter_by(id=role_id).first()
    if user and role:
        user.role.append(role)
session.commit()

print("Data loaded successfully.")
