import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI')
    SECRET_KEY = os.environ.get('FLASK_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False