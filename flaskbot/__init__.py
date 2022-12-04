import os

from dash import Dash
from dotenv import find_dotenv, load_dotenv
from flask import Flask
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy

load_dotenv(find_dotenv())

server = Flask(__name__)

app = Dash(
    __name__,
    server=server,
    url_base_pathname="/admin/dash/genre/",
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
)


babel = Babel(server)

basedir = os.path.abspath(os.path.dirname(__file__))

server.config["FLASK_ADMIN_SWATCH"] = "cerulean"
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
server.config["SECRET_KEY"] = os.getenv("secret_key")
server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.db"
)


db = SQLAlchemy(server)
from .admin import *
from .analytics import *
from .bot import *
