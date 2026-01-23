from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
flask_app = Flask(__name__)
login_manager = LoginManager()