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

from .other import AdminProfile, Product, FavoritesProducts

load_dotenv(find_dotenv())
login_manager = LoginManager(app)
bot = telebot.TeleBot(os.getenv("token"))

###########################################################################

STATE_DICT = {}
DEL_MESSEGE_ID = []

# STATE_DICT сохраняет состояние между обработчиками о текущем товаре

# DEL_MESSEGE_ID хранит идентификаторы предыдущих сообщений для удаления

###########################################################################

inline_back = types.InlineKeyboardButton(text="назад", callback_data="back")
inline_next = types.InlineKeyboardButton(text="вперед", callback_data="next")
inline_favorite = types.InlineKeyboardButton(text="\u2605", callback_data="favorite")
inline_del_favorite = types.InlineKeyboardButton(text="\u2605 \u2326", callback_data="delfavorite")
inline_pay = types.InlineKeyboardButton(text="Купить", callback_data="pay")

# клавиатура товара с "добавить в избраное"
markup_product_1 = types.InlineKeyboardMarkup()
# клавиатура товара с "убрать из избраное"
markup_product_2 = types.InlineKeyboardMarkup()
markup_product_1.add(inline_back, inline_next).add(inline_del_favorite, inline_pay)
markup_product_2.add(inline_back, inline_next).add(inline_favorite, inline_pay)

# ___________________________________________________________________________


@bot.message_handler(commands=["start"])
def start_chat(message):
    bot.send_message(message.from_user.id, message)


@bot.message_handler(commands=["product"])
#@bot.message_handler(content_types=["text"])
def get_product(message):
    list_products = deque(Product.query.filter_by(is_published=True).all())
    STATE_DICT.clear()
    STATE_DICT["list_products"] = list_products
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(user=message.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        markup_product = markup_product_1
    elif len(check) == 0:
        markup_product = markup_product_2
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.send_media_group(message.chat.id, media)
    bot.send_message(
        message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID.append(message.message_id + 1), DEL_MESSEGE_ID.append(
        message.message_id + 2
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'next')
def get_next_product(callback):
    try:
        list_products = STATE_DICT["list_products"]
    except:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    list_products.rotate(1)
    current_product = list_products[0]
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        markup_product =  markup_product_1
    elif len(check) == 0:
        markup_product = markup_product = markup_product_2
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    


@bot.callback_query_handler(func=lambda callback: callback.data == 'back')
def get_back_product(callback):
    try:
        list_products = STATE_DICT["list_products"]
    except:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    list_products.rotate(-1)
    current_product = list_products[0]
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        markup_product = markup_product_1
    elif len(check) == 0:
        markup_product = markup_product = markup_product_2
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'pay')
def make_pay_product(callback):
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    DEL_MESSEGE_ID.append(callback.message.message_id + 1)
    pay_product = STATE_DICT["list_products"][0]
    markup_product = types.InlineKeyboardMarkup()
    inline_back = types.InlineKeyboardButton(text="назад", callback_data="back")
    inline_next = types.InlineKeyboardButton(text="вперед", callback_data="next")
    markup_product.add(inline_back, inline_next)
    bot.send_message(callback.from_user.id, f" Книга <b>{pay_product.name}</b> куплена!", parse_mode="HTML", reply_markup=markup_product)


@bot.callback_query_handler(func=lambda callback: callback.data == 'favorite')
def set_favorite(callback):
    '''
    Добавление товара в список избранного.
    '''
    try:
        list_products = STATE_DICT["list_products"]
    except:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    current_product = list_products[0]
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )
    data_product = FavoritesProducts(user=callback.from_user.id,id_product=current_product.id, name=callback.from_user.first_name)
    db.session.add(data_product)
    db.session.commit()
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product_1,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'delfavorite')
def del_favorite(callback):
    '''
    Удаление товара из списка избранного.
    '''
    try:
        list_products = STATE_DICT["list_products"]
    except:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    current_product = list_products[0]
    images = [i.image for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    data_product = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id, name=callback.from_user.first_name).first()
    db.session.delete(data_product)
    db.session.commit()
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product_2,
    )
    

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
            flash("Неверный логин или пароль!")

    return render_template("autorization.html", title="Авторизация")


@app.route("/exit", methods=["POST", "GET"])
@login_required
def user_exit():
    logout_user()
    return redirect(url_for("index_autorization"))
