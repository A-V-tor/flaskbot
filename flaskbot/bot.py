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

from flaskbot import app, babel, db

from .other import AdminProfile, Product, FavoritesProducts, markup_product_1, markup_product_2, cat_keyboard, piligrim_keyboard_1, piligrim_keyboard_2, welcome_keyboard, favorites_keyboard



load_dotenv(find_dotenv())
login_manager = LoginManager(app)
bot = telebot.TeleBot(os.getenv("token"))




###########################################################################

STATE_DICT = {}
# STATE_DICT сохраняет состояние между обработчиками о текущем товаре

DEL_MESSEGE_ID = []
# DEL_MESSEGE_ID хранит идентификаторы предыдущих сообщений для удаления

CATEGORIES_DICT = {}
# хранение товаров по жанру

NAME_IMAGE = {}
# хранение имен изображений

# ###########################################################################


@bot.message_handler(commands=["start"])
def start_chat(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_message(message.from_user.id, ' Меню', reply_markup=welcome_keyboard)



@bot.callback_query_handler(func=lambda callback: callback.data == 'close')
def close_chat(callback):
    '''
    Закрытие чата по основному проходу товаров
    '''
    STATE_DICT["list_products"] = None
    CATEGORIES_DICT["genre"] = None
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()


@bot.callback_query_handler(func=lambda callback: callback.data == 'close-start')
def close_chat_start(callback):
    '''
    Закрытие стартового окна 
    '''
    bot.delete_message(callback.message.chat.id, callback.message.message_id)


@bot.callback_query_handler(func=lambda callback: callback.data == 'product')
def get_product(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    list_products = deque(Product.query.filter_by(is_published=True).all())
    STATE_DICT.clear()
    STATE_DICT["list_products"] = list_products
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        markup_product = markup_product_1
    elif len(check) == 0:
        markup_product = markup_product_2
    images = [i.name for i in current_product.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=markup_product,
    )
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'next')
def get_next_product(callback):
    print(1)
    if STATE_DICT["list_products"]:
        list_products = STATE_DICT["list_products"]
        print(2.0)
    else:
        list_products = deque(Product.query.filter_by(is_published=True).all())
        print(2.1)
    list_products.rotate(1)
    print(3)
    current_product = list_products[0]
    print(4)
    images = [i.name for i in current_product.image]
    print(5)
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    print(6)
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    print(7)
    if len(check) > 0:
        markup_product =  markup_product_1
        print(8)
    elif len(check) == 0:
        markup_product = markup_product = markup_product_2
        print(9)
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    print(10)
    DEL_MESSEGE_ID.clear()
    print(11)
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )
    print(12)
    bot.send_media_group(callback.message.chat.id, media)
    print(13)
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
    images = [i.name for i in current_product.image]
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
    images = [i.name for i in current_product.image]
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
    images = [i.name for i in current_product.image]
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


# _________________________________________________ХЕНДЛЕРЫ КАТЕГОРИЙ_________________________________________


@bot.callback_query_handler(func=lambda callback: callback.data == 'close-categories')
def close_chat_categories(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)



@bot.callback_query_handler(func=lambda callback: callback.data == 'categories')
def get_product_categories(callback):
    categories_novel = Product.query.filter_by(genre="Роман", is_published=True).all()
    categories_adventures = Product.query.filter_by(genre="Приключения", is_published=True).all()
    categories_fantasy = Product.query.filter_by(genre="Фэнтези", is_published=True).all()
    categories_thriller = Product.query.filter_by(genre="Триллер", is_published=True).all()
    categories_detective = Product.query.filter_by(genre="Детектив", is_published=True).all()
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    DEL_MESSEGE_ID.append(callback.message.message_id + 1)
    bot.send_message(
        callback.message.chat.id,
        f"<b>Категория</b>\n Роман {len(categories_novel)} шт \n Приключения {len(categories_adventures)} шт \n Фэнтези {len(categories_fantasy)} шт \n Триллер {len(categories_thriller)} шт \n Детектив {len(categories_detective)} шт \n",
        parse_mode="HTML",
        reply_markup=cat_keyboard,
    )


@bot.callback_query_handler(func=lambda callback: callback.data in ['adventures', 'novel', 'fantasy', 'thriller','detective'])
def get_selected_genre(callback):
    CATEGORIES_DICT['genre'] = None
    if callback.data == 'adventures':
        CATEGORIES_DICT['genre'] = deque(Product.query.filter_by(genre="Приключения", is_published=True).all())
    elif callback.data == 'novel':
        CATEGORIES_DICT['genre'] = deque(Product.query.filter_by(genre="Роман", is_published=True).all())
    elif callback.data == 'fantasy':
        CATEGORIES_DICT['genre'] = deque(Product.query.filter_by(genre="Фэнтези", is_published=True).all())
    elif callback.data == 'thriller':
        CATEGORIES_DICT['genre'] = deque(Product.query.filter_by(genre="Триллер", is_published=True).all())
    elif callback.data == 'detective':
        CATEGORIES_DICT['genre'] = deque(Product.query.filter_by(genre="Детектив", is_published=True).all())
    if len(CATEGORIES_DICT['genre']):
        current_product = CATEGORIES_DICT['genre'][0]
        check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
        if len(check) > 0:
            reply_markup = piligrim_keyboard_2
        elif len(check) == 0:
            reply_markup = piligrim_keyboard_1
        images = [i.name for i in current_product.image]
        media = [
            types.InputMediaPhoto(i)
            for i in [
                open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
                for i in images
        ]
    ]
        bot.send_media_group(callback.message.chat.id, media)
        bot.send_message(
            callback.message.chat.id,
            f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
            parse_mode="HTML",
            reply_markup=reply_markup,
    )
        [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
        DEL_MESSEGE_ID.clear()
        DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
            callback.message.message_id + 2) 
    else:
        bot.send_message(callback.message.chat.id, 'Пустой раздел.')
        DEL_MESSEGE_ID.append(callback.message.message_id + 1)


@bot.callback_query_handler(func=lambda callback: callback.data == 'cat-back')
def get_back_product_for_genry(callback):
    list_products = CATEGORIES_DICT['genre']
    list_products.rotate(-1)
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_2
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_1
    images = [i.name for i in current_product.image]
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
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'cat-next')
def get_next_product_for_genry(callback):
    list_products = CATEGORIES_DICT['genre']
    list_products.rotate(1)
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_2
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_1
    images = [i.name for i in current_product.image]
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
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_product.name}</b>,\n<i>{current_product.description}</i>,\n жанр: {current_product.genre},\n цена: <code>{current_product.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'cat-favorite')
def set_favorite(callback):
    '''
    Добавление товара в список избранного.
    '''
    list_products = CATEGORIES_DICT["genre"]
    current_product = list_products[0]
    images = [i.name for i in current_product.image]
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
        reply_markup=piligrim_keyboard_1,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'cat-del-favorite')
def del_favorite(callback):
    '''
    Удаление товара из списка избранного.
    '''
    list_products = CATEGORIES_DICT["genre"]
    current_product = list_products[0]
    images = [i.name for i in current_product.image]
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
        reply_markup=piligrim_keyboard_2,
    )


# _______________________________________ХЕНДЛЕРЫ ИЗБРАННОГО_______________________________

@bot.callback_query_handler(func=lambda callback: callback.data == 'get-favorites')
def get_favorites(callback):
    '''
    Простмотр списка избранное.
    '''
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    list_favorites = deque(FavoritesProducts.query.filter_by(user=callback.from_user.id).all())
    if not list_favorites:
        bot.send_message(callback.message.chat.id, 'У вас нет избранных товаров!')
        time.sleep(3)
        bot.delete_message(callback.message.chat.id, callback.message.message_id + 1)
    STATE_DICT["list_favorites"] = list_favorites
    current_favorites = list_favorites[0].product
    images = [i.name for i in current_favorites.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard
    )
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'fav-next')
def get_next_favorites(callback):
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    list_favorites = STATE_DICT["list_favorites"]
    list_favorites.rotate(1)
    print(1)
    current_favorites = list_favorites[0].product
    print(2)
    images = [i.name for i in current_favorites.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard
    )
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'fav-back')
def get_next_favorites(callback):
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    list_favorites = STATE_DICT["list_favorites"]
    list_favorites.rotate(-1)
    current_favorites = list_favorites[0].product
    images = [i.name for i in current_favorites.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard
    )
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'fav-del')
def get_next_favorites(callback):
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    list_favorites = STATE_DICT["list_favorites"]
    current_favorites = list_favorites[0].product
    data_product = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_favorites.id, name=callback.from_user.first_name).first()
    db.session.delete(data_product)
    db.session.commit()
    list_favorites.rotate(1)
    current_favorites = list_favorites[0].product
    if not current_favorites:
        bot.send_message(callback.message.chat.id, 'У вас нет избранных товаров!')
        time.sleep(3)
        bot.delete_message(callback.message.chat.id, callback.message.message_id + 1)
    images = [i.name for i in current_favorites.image]
    media = [
        types.InputMediaPhoto(i)
        for i in [
            open(f"{os.path.dirname(__file__)}/static/image-product/{i}", "rb")
            for i in images
        ]
    ]
    bot.send_media_group(callback.message.chat.id, media)
    bot.send_message(
        callback.message.chat.id,
        f"<b>НАЗВАНИЕ: {current_favorites.name}</b>,\n<i>{current_favorites.description}</i>,\n жанр: {current_favorites.genre},\n цена: <code>{current_favorites.price} ед.</code>",
        parse_mode="HTML",
        reply_markup=favorites_keyboard
    )
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(
        callback.message.message_id + 2
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

