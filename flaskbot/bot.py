import os
from collections import deque

import telebot
from dotenv import find_dotenv, load_dotenv
from flask import abort, request
from telebot import types

from flaskbot import app, db

from .other import Product

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv("token"))
STATE_DICT = {}


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.from_user.id, message)


@bot.message_handler(commands=["product"])
def get_product(message):
    '''
    Запуск прохода по списку товаров,

    STATE_DICT хранит список между обработчиками.
    '''
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
    # bot.delete_message(message.chat.id, message.message_id - 1)
    bot.send_media_group(message.chat.id, media)
    bot.send_message(
        message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup,
    )


@bot.message_handler(commands=["next"])
def get_next_product(message):
    '''
    Прокрутка списка вперед и отправка текущей еденицы товара.
    '''
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
    bot.send_media_group(message.chat.id, media)
    bot.send_message(
        message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup,
    )


@bot.message_handler(commands=["back"])
def get_next_product(message):
    '''
    Прокрутка списка назад и отправка текущей еденицы товара.
    '''
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
    bot.send_media_group(message.chat.id, media)
    bot.send_message(
        message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup,
    )


@bot.message_handler(commands=["pay"])
def make_pay_product(message):
    list_products = STATE_DICT["list_products"][0]
    bot.send_message(message.from_user.id, f" Книга '{list_products.name}' куплена!")


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        abort(403)
