import time
from collections import Counter
from datetime import datetime, timedelta
import dash_auth
import numpy as np
import pandas as pd
import plotly.express as px
import pytz
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from sqlalchemy import text
from flaskbot import app, db, app2, app3
from sqlalchemy import func
from .other import DashProfile, Product, CurrentDayUsers, FavoritesProducts

VALID_USERNAME_PASSWORD_PAIRS = {
    f"{DashProfile.query.filter_by().first().name}": f"{DashProfile.query.filter_by().first().psw}"
}


# dash_auth.BasicAuth(app2, VALID_USERNAME_PASSWORD_PAIRS)
# dash_auth.BasicAuth(app3, VALID_USERNAME_PASSWORD_PAIRS)
#dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)


def get_analytics_for_genre():
    count_genre = Product.query.filter_by(is_published=True).all()
    data = Counter([i.genre for i in count_genre])
    fig = px.bar({"Жанр": [*data.keys()], "Кол-во": [*data.values()] }, x="Жанр", y="Кол-во",  barmode="group")
    colors = {
        'background': 'white',
        'text': 'black',
    }
    fig.update_layout(
        title='☆',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    app.layout = html.Div(
            children=[
                html.Button('Обновить данные из бд', id='show-secret'),
                html.Div(id='body-div'),
                html.H1(children="Книги",style={
                'textAlign': 'center',
                'color': colors['text']
            }),
                html.A(children="назад", href="/admin/analytics/", style={'fontSize': '20px'}),
                html.Div(
                    children="""
                Статистика книг по жанру
            """,
            style={
                'textAlign': 'center',
                'color': colors['text'],
            }
                ),
                dcc.Graph(
                    id="example-graph",
                    figure=fig,
                ),
                dcc.Interval( 
                id = 'graph-update', 
                interval = 1*1000, 
                n_intervals = 0
            ),
            ]
        )

@app.callback(
    Output(component_id='body-div', component_property='children'),
    [Input(component_id='show-secret', component_property='n_clicks')]
)

def update_output(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        get_analytics_for_genre()
        return 'Обновите окно браузера'



def get_visit_statistics():
    sql_data_for_visits = text('SELECT strftime("%Y-%m-%d",date) FROM  current_day_product GROUP BY date')
    sql_data_for_visits_premium = text('SELECT strftime("%Y-%m-%d",date) FROM  current_day_product WHERE is_premium=True GROUP BY date')
    sql_data_for_visits_bot = text('SELECT strftime("%Y-%m-%d",date) FROM  current_day_product WHERE is_bot=True GROUP BY date')
    amount_visits_users_premium = Counter([i[0] for i in db.engine.execute(sql_data_for_visits_premium)])
    amount_visits_users = Counter([i[0] for i in db.engine.execute(sql_data_for_visits)])
    amount_visits_bot = Counter([i[0] for i in db.engine.execute(sql_data_for_visits_bot)])

    app2.layout = html.Div(
        [html.Button('Обновить данные из бд', id='show-secret'),
        html.Div(id='body-div'),
            html.H2(
            'Динамика посещений',
        ),
        html.A(children="назад", href="/admin/analytics/", style={'fontSize': '20px'}),
        dcc.Graph(
            id="graph",
            figure={
                        "data": [
                            {
                                "x": [*amount_visits_users.keys()],
                                "y": [*amount_visits_users.values()],
                                "type": "line",
                                "name": "Всего",
                            },
                            {
                                "x": [*amount_visits_users_premium.keys()],
                                "y": [*amount_visits_users_premium.values()],
                                "type": "line",
                                "name": "Премиум", 
                            },
                            {
                                "x": [*amount_visits_bot.keys()],
                                "y": [*amount_visits_bot.values()],
                                "type": "line",
                                "name": "Роботы", 
                            }
                        ],
                        "layout": {"title": "Пользователи"},
                    }
        ),
        dcc.Interval( 
                id = 'graph-update', 
                interval = 1*1000, 
                n_intervals = 0
                )
        ]
    )

@app2.callback(
    Output(component_id='body-div', component_property='children'),
    [Input(component_id='show-secret', component_property='n_clicks')]
)

def update_output(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        get_visit_statistics()
        return 'Обновите окно браузера'



def get_favorite():
    data_selected = db.session.query(FavoritesProducts.id_product, func.count(FavoritesProducts.id_product)).group_by(FavoritesProducts.id_product).all()
    sl = {}
    for i in data_selected:
        sql = Product.query.filter_by(id=i[0]).first().name
        sl[sql] = i[1]


    fig = px.bar({"Книга": [*sl.keys()], "Кол-во": [*sl.values()], }, x="Книга", y="Кол-во")

    app3.layout = html.Div([
        html.Button('Обновить данные из бд', id='show-secret'),
        html.Div(id='body-div'),
        html.H2('Популярность товара'),
        html.A(children="назад", href="/admin/analytics/", style={'fontSize': '20px'}),
        dcc.Graph(
            id='graph',
            figure=fig
        )
    ])

@app3.callback(
    Output(component_id='body-div', component_property='children'),
    [Input(component_id='show-secret', component_property='n_clicks')]
)

def update_output(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        get_favorite()
        return 'Обновите окно браузера'


get_analytics_for_genre()
get_visit_statistics()
get_favorite()