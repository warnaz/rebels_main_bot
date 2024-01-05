import logging
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename='sqlalchemy.log', level=logging.INFO)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

DB_LOGIN, DB_PASSWORD = os.getenv('DB_LOGIN'), os.getenv('DB_PASSWORD')
DB_HOST, DB_PORT = os.getenv('DB_HOST'), os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

url = f'postgresql+asyncpg://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_async_engine(url=url, echo=True)

session = sessionmaker(engine)
Base = declarative_base()
