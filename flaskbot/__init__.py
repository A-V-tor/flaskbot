import os

from dotenv import find_dotenv, load_dotenv
from flask import Flask
from dash import Dash
from flask_babelex import Babel
from flask_sqlalchemy import SQLAlchemy


load_dotenv(find_dotenv())

server = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(
    __name__,
    server=server,
    url_base_pathname='/admin/dash/genre/',
    external_stylesheets = external_stylesheets
)
#app.config.suppress_callback_exceptions = True

app2 = Dash(
    __name__,
    server=server,
    url_base_pathname='/admin/dash/current-day/',
    external_stylesheets = external_stylesheets
)

app3 = Dash(
    __name__,
    server=server,
    url_base_pathname='/admin/dash/favorites/',
    external_stylesheets = external_stylesheets
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
from .analytics import *
from .admin import *
from .bot import *
