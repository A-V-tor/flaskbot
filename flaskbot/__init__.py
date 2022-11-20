import os

from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy

load_dotenv(find_dotenv())
app = Flask(__name__)
babel = Babel(app)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.db"
)


db = SQLAlchemy(app)
from .admin import *
from .bot import *
