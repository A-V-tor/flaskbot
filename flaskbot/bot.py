import os
from collections import deque

import telebot
from dotenv import find_dotenv, load_dotenv
from flask import abort, flash, redirect, render_template, request, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from telebot import types

from flaskbot import app, babel, db

from .other import AdminProfile, Product

load_dotenv(find_dotenv())
login_manager = LoginManager(app)
bot = telebot.TeleBot(os.getenv("token"))

###########################################################################

STATE_DICT = {}
DEL_MESSEGE_ID = []

# STATE_DICT сохраняет состояние между обработчиками о текущем товаре

# DEL_MESSEGE_ID хранит идентификаторы предыдущих сообщений для удаления

###########################################################################


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.from_user.id, message)


@bot.message_handler(commands=["product"])
def get_product(message):
    """
    Запуск прохода по списку товаров.
    """
    list_products = deque(Product.query.filter_by(is_published=True).all())
    STATE_DICT["list_products"] = list_products
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    but_next = types.KeyboardButton("/next")
    but_pay = types.KeyboardButton("/pay")
    markup.add(but_next).add(but_pay)
    current_product = list_products[0]
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_media_group(message.chat.id, media)
    bot.send_message(
        message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup,
    )
    DEL_MESSEGE_ID.append(message.message_id + 1), DEL_MESSEGE_ID.append(
        message.message_id + 2
    )


@bot.message_handler(commands=["next"])
def get_next_product(message):
    """
    Прокрутка списка вперед и отправка текущей еденицы товара.

    Удаляются сообщения о предыдущем товаре.
    """
    [bot.delete_message(message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    DEL_MESSEGE_ID.append(message.message_id + 1), DEL_MESSEGE_ID.append(
        message.message_id + 2
    )
    list_products = STATE_DICT["list_products"]
    list_products.rotate(1)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    but_back = types.KeyboardButton("/back")
    but_next = types.KeyboardButton("/next")
    but_pay = types.KeyboardButton("/pay")
    markup.add(but_next).add(but_back).add(but_pay)
    current_product = list_products[0]
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_media_group(message.chat.id, media)
    bot.send_message(
        message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup,
    )


@bot.message_handler(commands=["back"])
def get_next_product(message):
    """
    Прокрутка списка назад и отправка текущей еденицы товара.

    Удаляются сообщения о предыдущем товаре.
    """
    [bot.delete_message(message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    DEL_MESSEGE_ID.append(message.message_id + 1), DEL_MESSEGE_ID.append(
        message.message_id + 2
    )
    list_products = STATE_DICT["list_products"]
    list_products.rotate(-1)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    but_back = types.KeyboardButton("/back")
    but_next = types.KeyboardButton("/next")
    but_pay = types.KeyboardButton("/pay")
    markup.add(but_next).add(but_back).add(but_pay)
    current_product = list_products[0]
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_media_group(message.chat.id, media)
    bot.send_message(
        message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup,
    )


@bot.message_handler(commands=["pay"])
def make_pay_product(message):
    pay_product = STATE_DICT["list_products"][0]
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.from_user.id, f" Книга '{pay_product.name}' куплена!")


@login_manager.user_loader
def load_user(user):
    return AdminProfile.query.get(user)


@babel.localeselector
def get_locale():
    if request.args.get("lang"):
        session["lang"] = request.args.get("lang")
    return session.get("lang", "ru")


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        abort(403)


@app.route("/login", methods=["POST", "GET"])
def index_autorization():
    """Авторизация администратора"""

    if request.method == "POST":
        datauser = AdminProfile.query.filter_by(
            name=request.form["name"], psw=request.form["psw"]
        ).first()
        if datauser:
            login_user(datauser, remember=True)
            return redirect(url_for("admin.index"))
        else:
            print("что то не так")
            flash("Неверный логин или пароль!")

    return render_template("autorization.html", title="Авторизация")


@app.route("/exit", methods=["POST", "GET"])
@login_required
def user_exit():
    logout_user()
    return redirect(url_for("index_autorization"))
