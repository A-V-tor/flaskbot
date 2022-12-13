from collections import Counter
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from sqlalchemy import text
from flaskbot import app, db, app2, app3, server
from sqlalchemy import func
from .other import Product, FavoritesProducts
from flask_login import current_user





def get_analytics_for_genre(server):

    app.layout = html.Div(
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(id="my-header", className="text-center"),
                        ],
                        className="col-md-12",
                    )
                ],
                className="row",
            ),
            html.A("Войти", id="login-link", href="/login"),
            html.Div(id="my-div", className="text-center"),
            html.Button(
                id="submit-button-state",
                n_clicks=1,
                children="Submit",
                style={"display": "none"},
            ),
        ]
    )

    @app.callback(
        [
            Output(component_id="my-header", component_property="children"),
            Output(component_id="my-div", component_property="children"),
            Output(component_id="login-link", component_property="style"),
        ],
        [Input(component_id="submit-button-state", component_property="n_clicks")],
    )

    def get_user_name(n_clicks):
        if current_user.admin:
            welcome_msg = "Авторизованы как, " + current_user.name
            user_data = get_analytics_for_genre()
            link_style = {"display": "none"}
            return welcome_msg, user_data, link_style
        return "Your Princess is in another castle", ""
    def get_analytics_for_genre():
        count_genre = Product.query.filter_by(is_published=True).all()
        data = Counter([i.genre for i in count_genre])
        fig = px.bar(
            {"Жанр": [*data.keys()], "Кол-во": [*data.values()]},
            x="Жанр",
            y="Кол-во",
            barmode="group",
        )
        colors = {
            "background": "white",
            "text": "black",
        }
        fig.update_layout(
            title="☆",
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
        )

        return html.Div(
            children=[
                html.Div(id="body-div"),
                html.H1(
                    children="Книги", style={"textAlign": "center", "color": colors["text"]}
                ),
                html.A(
                    children="назад", href="/admin/analytics/", style={"fontSize": "20px"}
                ),
                html.Div(
                    children="""
                    Статистика книг по жанру
                """,
                    style={
                        "textAlign": "center",
                        "color": colors["text"],
                    },
                ),
                dcc.Graph(
                    id="example-graph",
                    figure=fig,
                ),
                dcc.Interval(id="graph-update", interval=1 * 1000, n_intervals=0),
            ]
        )

    return app.server





def get_visit_statistics(server):

    app2.layout = html.Div(
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(id="my-header", className="text-center"),
                        ],
                        className="col-md-12",
                    )
                ],
                className="row",
            ),
            html.A("Войти", id="login-link", href="/login"),
            html.Div(id="my-div", className="text-center"),
            html.Button(
                id="submit-button-state",
                n_clicks=1,
                children="Submit",
                style={"display": "none"},
            ),
        ]
    )

    @app2.callback(
        [
            Output(component_id="my-header", component_property="children"),
            Output(component_id="my-div", component_property="children"),
            Output(component_id="login-link", component_property="style"),
        ],
        [Input(component_id="submit-button-state", component_property="n_clicks")],
    )

    def get_user_name(n_clicks):
        if current_user.admin:
            welcome_msg = "Авторизованы как, " + current_user.name
            user_data = get_visit_statistics()
            link_style = {"display": "none"}
            return welcome_msg, user_data, link_style
        return "Your Princess is in another castle", ""

    def get_visit_statistics():
        '''
        Статистика посещения по различным группам.

        '''
        
        sql_data_for_visits = text(
            'SELECT strftime("%Y-%m-%d",date) FROM  current_day_product GROUP BY date'
        )
        sql_data_for_visits_premium = text(
            'SELECT strftime("%Y-%m-%d",date) FROM  current_day_product WHERE is_premium=True GROUP BY date'
        )
        sql_data_for_visits_bot = text(
            'SELECT strftime("%Y-%m-%d",date) FROM  current_day_product WHERE is_bot=True GROUP BY date'
        )
        amount_visits_users_premium = Counter(
            [i[0] for i in db.engine.execute(sql_data_for_visits_premium)]
        )
        amount_visits_users = Counter(
            [i[0] for i in db.engine.execute(sql_data_for_visits)]
        )
        amount_visits_bot = Counter(
            [i[0] for i in db.engine.execute(sql_data_for_visits_bot)]
        )
        

        return html.Div(
            [
                html.Div(id="body-div"),
                html.H2(
                    "Динамика посещений",
                ),
                html.A(
                    children="назад", href="/admin/analytics/", style={"fontSize": "20px"}
                ),
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
                            },
                        ],
                        "layout": {"title": "Пользователи"},
                    },
                ),
                dcc.Interval(id="graph-update", interval=1 * 1000, n_intervals=0),
            ]
        )
        
    return app2.server
        
    

def get_favorite(server):
    app3.layout = html.Div(
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.H1(id="my-header", className="text-center"),
                        ],
                        className="col-md-12",
                    )
                ],
                className="row",
            ),
            html.A("Войти", id="login-link", href="/login"),
            html.Div(id="my-div", className="text-center"),
            html.Button(
                id="submit-button-state",
                n_clicks=1,
                children="Submit",
                style={"display": "none"},
            ),
        ]
    )

    @app3.callback(
        [
            Output(component_id="my-header", component_property="children"),
            Output(component_id="my-div", component_property="children"),
            Output(component_id="login-link", component_property="style"),
        ],
        [Input(component_id="submit-button-state", component_property="n_clicks")],
    )

    def get_user_name(n_clicks):
        if current_user.admin:
            welcome_msg = "Авторизованы как, " + current_user.name
            user_data =get_favorite()
            link_style = {"display": "none"}
            return welcome_msg, user_data, link_style
        return "Your Princess is in another castle", ""

    def get_favorite():
        data_selected = (
            db.session.query(
                FavoritesProducts.id_product, func.count(FavoritesProducts.id_product)
            )
            .group_by(FavoritesProducts.id_product)
            .all()
        )
        sl = {}
        for i in data_selected:
            sql = Product.query.filter_by(id=i[0]).first().name
            sl[sql] = i[1]

        fig = px.bar(
            {
                "Книга": [*sl.keys()],
                "Кол-во": [*sl.values()],
            },
            x="Книга",
            y="Кол-во",
        )

        return html.Div(
            [
                html.Div(id="body-div"),
                html.H2("Популярность товара"),
                html.A(
                    children="назад", href="/admin/analytics/", style={"fontSize": "20px"}
                ),
                dcc.Graph(id="graph", figure=fig),
            ]
        )

    return app3.server



get_analytics_for_genre(server)
get_favorite(server)
get_visit_statistics(server)