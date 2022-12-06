import datetime
import os
import time
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

from flaskbot import app, babel, db, server

from .other import (
    AdminProfile,
    CurrentDayUsers,
    FavoritesProducts,
    Product,
    cat_keyboard,
    favorites_keyboard,
    markup_product_1,
    markup_product_2,
    piligrim_keyboard,
    piligrim_keyboard_1,
    piligrim_keyboard_2,
    search_keyboard,
    search_keyboard_1,
    search_keyboard_2,
    welcome_keyboard,
)

load_dotenv(find_dotenv())
login_manager = LoginManager(server)
bot = telebot.TeleBot(os.getenv("token"))


###########################################################################

STATE_DICT = {}
# STATE_DICT сохраняет состояние между обработчиками о текущем товаре

DEL_MESSEGE_ID = {}
# DEL_MESSEGE_ID хранит идентификаторы предыдущих сообщений для удаления

CATEGORIES_DICT = {}
# хранение товаров по жанру

SEARCH_DICT = {}
# хранение товаров поиска

# ###########################################################################


@bot.message_handler(commands=["start"])
def start_chat(message):
    user = message.from_user.id
    is_premium = message.from_user.is_premium
    is_bot = message.from_user.is_bot
    language_code = message.from_user.language_code
    check = CurrentDayUsers.query.filter_by(user=user).order_by(CurrentDayUsers.date.desc()).first()
    if is_premium == None:
        is_premium = False
    else:
        is_premium = True
    if check and check.date.strftime("%Y-%m-%d") < datetime.datetime.now().strftime(
        "%Y-%m-%d"
    ):
        data_for_entries = CurrentDayUsers(
            user=user, is_premium=is_premium, is_bot=is_bot, language_code=language_code
        )
        db.session.add(data_for_entries)
    elif not check:
        data_for_entries = CurrentDayUsers(
            user=user, is_premium=is_premium, is_bot=is_bot, language_code=language_code
        )
        db.session.add(data_for_entries)
    db.session.commit()
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(
        message.from_user.id,
        '<b>Меню</b>\n\n 🎁 - список товаров\n\n 🚥 - категории товара\n\n ✨✨✨ - список избранного\n\n для 🔍 введите команду "/start" и через пробел название книги или перове слово названия',
        reply_markup=welcome_keyboard,
        parse_mode="HTML",
    )


@bot.callback_query_handler(func=lambda callback: callback.data == "close")
def close_chat(callback):
    """
    Закрытие чата по основному проходу товаров
    """
    STATE_DICT[callback.from_user.id] = {"list_products": None}
    CATEGORIES_DICT[callback.from_user.id] = {"genre": None}
    SEARCH_DICT[callback.from_user.id] = None
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()


@bot.callback_query_handler(func=lambda callback: callback.data == "close-start")
def close_chat_start(callback):
    """
    Закрытие стартового окна
    """
    bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.message_handler(commands=["a"])
def help_chat(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.from_user.id, message.from_user)


# __________________________________________ХЕНДЛЕРЫ ПОИСКА_____________________________________________________________


@bot.message_handler(commands=["search"])
def start_search(message):
    bot.delete_message(message.chat.id, message.message_id)
    data_for_search = message.text.split(" ")[1]
    search_list = deque(
        Product.query.filter(
            Product.name.ilike(f"%{data_for_search.capitalize()}%")
        ).all()
    )
    DEL_MESSEGE_ID[message.from_user.id] = []
    if search_list:
        SEARCH_DICT[message.from_user.id] = search_list
        current_product = search_list[0]
        check = FavoritesProducts.query.filter_by(
            user=message.from_user.id, id_product=current_product.id
        ).all()
        if len(check) > 0:
            markup_product = search_keyboard_1
        elif len(check) == 0:
            markup_product = search_keyboard_2
        with open(
            f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
            "rb",
        ) as photo:
            item_id_photo = bot.send_photo(message.chat.id, photo=photo)
        item_id_text = bot.send_message(
            message.chat.id,
            f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
            parse_mode="HTML",
            reply_markup=markup_product,
        )
        DEL_MESSEGE_ID[message.from_user.id].append(
            item_id_photo.message_id
        ), DEL_MESSEGE_ID[message.from_user.id].append(item_id_text.message_id)
    else:
        item_id_text = bot.send_message(message.from_user.id, "не найденно")
        DEL_MESSEGE_ID[message.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "search-next")
def next_search(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    search_list = SEARCH_DICT[callback.from_user.id]
    search_list.rotate(1)
    current_product = search_list[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        markup_product = search_keyboard_1
    elif len(check) == 0:
        markup_product = search_keyboard_2
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "search-back")
def back_search(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    search_list = SEARCH_DICT[callback.from_user.id]
    search_list.rotate(-1)
    current_product = search_list[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        markup_product = search_keyboard_1
    elif len(check) == 0:
        markup_product = search_keyboard_2
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "search-pay")
def back_search(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    pay_product = SEARCH_DICT[callback.from_user.id][0]
    item_id_text = bot.send_message(
        callback.from_user.id,
        f" Книга <b>{pay_product.name}</b> куплена!",
        parse_mode="HTML",
        reply_markup=search_keyboard,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "search-favorite")
def favorite_search(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    search_list = SEARCH_DICT[callback.from_user.id]
    current_product = search_list[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        markup_product = search_keyboard_2
    elif len(check) == 0:
        markup_product = search_keyboard_1
    data_product = FavoritesProducts(
        user=callback.from_user.id,
        id_product=current_product.id,
        name=callback.from_user.first_name,
    )
    db.session.add(data_product)
    db.session.commit()
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(
    func=lambda callback: callback.data == "search-del-favorite"
)
def del_favorite_search(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    search_list = SEARCH_DICT[callback.from_user.id]
    current_product = search_list[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        markup_product = search_keyboard_2
    elif len(check) == 0:
        markup_product = search_keyboard_1
    data_product = FavoritesProducts.query.filter_by(
        user=callback.from_user.id,
        id_product=current_product.id,
        name=callback.from_user.first_name,
    ).first()
    db.session.delete(data_product)
    db.session.commit()
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


# ________________________________________________ОСНОВНЫЕ ХЕНДЛЕРЫ_______________________________________________________


@bot.callback_query_handler(func=lambda callback: callback.data == "product")
def get_product(callback):
    DEL_MESSEGE_ID[callback.from_user.id] = []
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    list_products = deque(Product.query.filter_by(is_published=True).all())
    STATE_DICT[callback.from_user.id] = {"list_products": list_products}
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        markup_product = markup_product_1
    elif len(check) == 0:
        markup_product = markup_product_2
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(
            callback.message.chat.id,
            photo=photo,
        )
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "next")
def get_next_product(callback):
    if STATE_DICT[callback.from_user.id]["list_products"]:
        list_products = STATE_DICT[callback.from_user.id]["list_products"]
    else:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    list_products.rotate(1)
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        markup_product = markup_product_1
    elif len(check) == 0:
        markup_product = markup_product = markup_product_2
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "back")
def get_back_product(callback):
    try:
        list_products = STATE_DICT[callback.from_user.id]["list_products"]
    except:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    list_products.rotate(-1)
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        markup_product = markup_product_1
    elif len(check) == 0:
        markup_product = markup_product = markup_product_2
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "pay")
def make_pay_product(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    pay_product = STATE_DICT[callback.from_user.id]["list_products"][0]
    markup_product = types.InlineKeyboardMarkup()
    inline_back = types.InlineKeyboardButton(text="назад", callback_data="back")
    inline_next = types.InlineKeyboardButton(text="вперед", callback_data="next")
    markup_product.add(inline_back, inline_next)
    item_id_text = bot.send_message(
        callback.from_user.id,
        f" Книга <b>{pay_product.name}</b> куплена!",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "favorite")
def set_favorite(callback):
    """
    Добавление товара в список избранного.
    """
    try:
        list_products = STATE_DICT[callback.from_user.id]["list_products"]
    except:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    current_product = list_products[0]
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    data_product = FavoritesProducts(
        user=callback.from_user.id,
        id_product=current_product.id,
        name=callback.from_user.first_name,
    )
    db.session.add(data_product)
    db.session.commit()
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product_1,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "delfavorite")
def del_favorite(callback):
    """
    Удаление товара из списка избранного.
    """
    try:
        list_products = STATE_DICT[callback.from_user.id]["list_products"]
    except:
        list_products = deque(Product.query.filter_by(is_published=True).all())
    current_product = list_products[0]
    data_product = FavoritesProducts.query.filter_by(
        user=callback.from_user.id,
        id_product=current_product.id,
        name=callback.from_user.first_name,
    ).first()
    db.session.delete(data_product)
    db.session.commit()
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product_2,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


# _________________________________________________ХЕНДЛЕРЫ КАТЕГОРИЙ_________________________________________


@bot.callback_query_handler(func=lambda callback: callback.data == "close-categories")
def close_chat_categories(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "categories")
def get_product_categories(callback):
    categories_novel = Product.query.filter_by(genre="Роман", is_published=True).all()
    categories_adventures = Product.query.filter_by(
        genre="Приключения", is_published=True
    ).all()
    categories_fantasy = Product.query.filter_by(
        genre="Фэнтези", is_published=True
    ).all()
    categories_thriller = Product.query.filter_by(
        genre="Триллер", is_published=True
    ).all()
    categories_detective = Product.query.filter_by(
        genre="Детектив", is_published=True
    ).all()
    categories_philosophy = Product.query.filter_by(
        genre="Философия", is_published=True
    ).all()
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>Категория</b>\n Роман {len(categories_novel)} шт \n Приключения {len(categories_adventures)} шт \n Фэнтези {len(categories_fantasy)} шт \n Триллер {len(categories_thriller)} шт \n Детектив {len(categories_detective)} шт \n Философия {len(categories_philosophy)}",
        parse_mode="HTML",
        reply_markup=cat_keyboard,
    )
    DEL_MESSEGE_ID[callback.from_user.id] = []
    DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(
    func=lambda callback: callback.data
    in ["adventures", "novel", "fantasy", "thriller", "detective", "philosophy"]
)
def get_selected_genre(callback):
    CATEGORIES_DICT[callback.from_user.id] = None
    if callback.data == "adventures":
        CATEGORIES_DICT[callback.from_user.id] = {
            "genre": deque(
                Product.query.filter_by(genre="Приключения", is_published=True).all()
            )
        }
    elif callback.data == "novel":
        CATEGORIES_DICT[callback.from_user.id] = {
            "genre": deque(
                Product.query.filter_by(genre="Роман", is_published=True).all()
            )
        }
    elif callback.data == "fantasy":
        CATEGORIES_DICT[callback.from_user.id] = {
            "genre": deque(
                Product.query.filter_by(genre="Фэнтези", is_published=True).all()
            )
        }
    elif callback.data == "thriller":
        CATEGORIES_DICT[callback.from_user.id] = {
            "genre": deque(
                Product.query.filter_by(genre="Триллер", is_published=True).all()
            )
        }
    elif callback.data == "detective":
        CATEGORIES_DICT[callback.from_user.id] = {
            "genre": deque(
                Product.query.filter_by(genre="Детектив", is_published=True).all()
            )
        }
    elif callback.data == "philosophy":
        CATEGORIES_DICT[callback.from_user.id] = {
            "genre": deque(
                Product.query.filter_by(genre="Философия", is_published=True).all()
            )
        }
    if len(CATEGORIES_DICT[callback.from_user.id]["genre"]):
        current_product = CATEGORIES_DICT[callback.from_user.id]["genre"][0]
        check = FavoritesProducts.query.filter_by(
            user=callback.from_user.id, id_product=current_product.id
        ).all()
        if len(check) > 0:
            reply_markup = piligrim_keyboard_2
        elif len(check) == 0:
            reply_markup = piligrim_keyboard_1
        photo = open(
            f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
            "rb",
        )
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
        item_id_text = bot.send_message(
            callback.message.chat.id,
            f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        DEL_MESSEGE_ID[callback.from_user.id].clear()
        DEL_MESSEGE_ID[callback.from_user.id].append(
            item_id_photo.message_id
        ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)
    else:
        item_id_text = bot.send_message(callback.message.chat.id, "Пустой раздел.")
        DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "cat-back")
def get_back_product_for_genry(callback):
    list_products = CATEGORIES_DICT[callback.from_user.id]["genre"]
    list_products.rotate(-1)
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_2
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_1
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "piligrim-pay")
def pay_for_genry(callback):
    list_products = CATEGORIES_DICT[callback.from_user.id]["genre"]
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    pay_product = list_products[0]
    item_id_text = bot.send_message(
        callback.from_user.id,
        f" Книга <b>{pay_product.name}</b> куплена!",
        parse_mode="HTML",
        reply_markup=piligrim_keyboard,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "cat-next")
def get_next_product_for_genry(callback):
    list_products = CATEGORIES_DICT[callback.from_user.id]["genre"]
    list_products.rotate(1)
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_2
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_1
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "cat-favorite")
def set_favorite(callback):
    """
    Добавление товара в список избранного.
    """
    list_products = CATEGORIES_DICT[callback.from_user.id]["genre"]
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_1
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_2
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    data_product = FavoritesProducts(
        user=callback.from_user.id,
        id_product=current_product.id,
        name=callback.from_user.first_name,
    )
    db.session.add(data_product)
    db.session.commit()
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "cat-del-favorite")
def del_favorite(callback):
    """
    Удаление товара из списка избранного.
    """
    list_products = CATEGORIES_DICT[callback.from_user.id]["genre"]
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(
        user=callback.from_user.id, id_product=current_product.id
    ).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_1
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_2
    data_product = FavoritesProducts.query.filter_by(
        user=callback.from_user.id,
        id_product=current_product.id,
        name=callback.from_user.first_name,
    ).first()
    db.session.delete(data_product)
    db.session.commit()
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_product.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


# _______________________________________ХЕНДЛЕРЫ ИЗБРАННОГО_______________________________


@bot.callback_query_handler(func=lambda callback: callback.data == "get-favorites")
def get_favorites(callback):
    """
    Простмотр списка избранное.
    """
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    list_favorites = deque(
        FavoritesProducts.query.filter_by(user=callback.from_user.id).all()
    )
    if not list_favorites:
        bot.send_message(callback.message.chat.id, "У вас нет избранных товаров!")
        time.sleep(3)
        bot.delete_message(callback.message.chat.id, callback.message.message_id + 1)
    STATE_DICT[callback.from_user.id] = {"list_favorites": list_favorites}
    current_favorites = list_favorites[0].product
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_favorites.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard,
    )
    DEL_MESSEGE_ID[callback.from_user.id] = []
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "fav-next")
def get_next_favorites(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    list_favorites = STATE_DICT[callback.from_user.id]["list_favorites"]
    list_favorites.rotate(1)
    current_favorites = list_favorites[0].product
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_favorites.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "fav-back")
def get_next_favorites(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    list_favorites = STATE_DICT[callback.from_user.id]["list_favorites"]
    list_favorites.rotate(-1)
    current_favorites = list_favorites[0].product
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_favorites.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == "fav-del")
def get_next_favorites(callback):
    [
        bot.delete_message(callback.message.chat.id, id)
        for id in DEL_MESSEGE_ID[callback.from_user.id]
    ]
    DEL_MESSEGE_ID[callback.from_user.id].clear()
    list_favorites = STATE_DICT[callback.from_user.id]["list_favorites"]
    current_favorites = list_favorites[0].product
    data_product = FavoritesProducts.query.filter_by(
        user=callback.from_user.id,
        id_product=current_favorites.id,
        name=callback.from_user.first_name,
    ).first()
    db.session.delete(data_product)
    db.session.commit()
    list_favorites = deque(
        FavoritesProducts.query.filter_by(user=callback.from_user.id).all()
    )
    STATE_DICT[callback.from_user.id] = {"list_favorites": list_favorites}
    # проблема с подгрузкой связаной таблицы
    current_favorites = list_favorites[0].product
    if not current_favorites:
        bot.send_message(callback.message.chat.id, "У вас нет избранных товаров!")
        time.sleep(3)
        bot.delete_message(callback.message.chat.id, callback.message.message_id + 1)
    with open(
        f"{os.path.dirname(__file__)}/static/image-product/{current_favorites.image}",
        "rb",
    ) as photo:
        item_id_photo = bot.send_photo(callback.message.chat.id, photo=photo)
    item_id_text = bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard,
    )
    DEL_MESSEGE_ID[callback.from_user.id].append(
        item_id_photo.message_id
    ), DEL_MESSEGE_ID[callback.from_user.id].append(item_id_text.message_id)


@login_manager.user_loader
def load_user(user):
    return AdminProfile.query.get(user)


@babel.localeselector
def get_locale():
    if request.args.get("lang"):
        session["lang"] = request.args.get("lang")
    return session.get("lang", "ru")


@server.route("/hello-world")
def hello():
    return "Hello World!"


@server.route("/", methods=["GET", "POST"])
def receive_update():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "123"
    else:
        abort(403)


@server.route("/login", methods=["POST", "GET"])
def index_autorization():
    """Авторизация администратора"""

    if request.method == "POST":
        datauser = AdminProfile.query.filter_by(
            name=request.form["name"], psw=request.form["psw"]
        ).first()
        if datauser:
            login_user(datauser, remember=True)
            session["admin"] = True
            return redirect(url_for("admin.index"))
        else:
            flash("Неверный логин или пароль!")

    return render_template("autorization.html", title="Авторизация")


@server.route("/exit", methods=["POST", "GET"])
@login_required
def user_exit():
    logout_user()
    session["admin"] = False
    return redirect(url_for("index_autorization"))


bot.remove_webhook()
time.sleep(0.1)

bot.set_webhook(url="")
