import time
from collections import Counter
from datetime import datetime

import dash_auth
import numpy as np
import pandas as pd
import plotly.express as px
import pytz
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from flaskbot import app, db

from .other import DashProfile, Product

VALID_USERNAME_PASSWORD_PAIRS = {
    f"{DashProfile.query.filter_by().first().name}": f"{DashProfile.query.filter_by().first().psw}"
}

auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)


def get_analytics_for_genre():
    print("_______")
    count_genre = Product.query.filter_by(is_published=True).all()

    data = Counter([i.genre for i in count_genre])
    app.layout = html.Div(
        children=[
            html.H1(children="Книги"),
            html.A(children="назад", href="/admin/analytics/"),
            html.Div(
                children="""
            Статистика книг по жанру
        """
            ),
            dcc.Graph(
                id="example-graph",
                figure={
                    "data": [
                        {
                            "x": [*data.keys()],
                            "y": [*data.values()],
                            "type": "bar",
                            "name": "Жанр",
                        },
                    ],
                    "layout": {"title": "в каждой категории представлено: "},
                },
            ),
        ]
    )


get_analytics_for_genre()
