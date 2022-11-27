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
# STATE_DICT сохраняет состояние между обработчиками о текущем товаре

DEL_MESSEGE_ID = []
# DEL_MESSEGE_ID хранит идентификаторы предыдущих сообщений для удаления

CATEGORIES_DICT = {}
# хранение товаров по жанру

# ###########################################################################

close_button = types.InlineKeyboardButton(text="закрыть", callback_data="close")
# клавиатура для прохода по списку товаров
inline_back = types.InlineKeyboardButton(text="назад", callback_data="back")
inline_next = types.InlineKeyboardButton(text="вперед", callback_data="next")
inline_favorite = types.InlineKeyboardButton(text="\u2605", callback_data="favorite")
inline_del_favorite = types.InlineKeyboardButton(text="\u2605 \u2326", callback_data="delfavorite")
inline_pay = types.InlineKeyboardButton(text="Купить", callback_data="pay")

# клавиатура товара с "добавить в избраное"
markup_product_1 = types.InlineKeyboardMarkup()
markup_product_1.add(inline_back, inline_next).add(inline_del_favorite, inline_pay).add(close_button)
# клавиатура товара с "убрать из избраное"
markup_product_2 = types.InlineKeyboardMarkup()
markup_product_2.add(inline_back, inline_next).add(inline_favorite, inline_pay).add(close_button)


# клавиатура показа категорий товара

category_adventures = types.InlineKeyboardButton(text="приключения", callback_data="adventures")
category_fantasy = types.InlineKeyboardButton(text="фентези", callback_data="fantasy")
category_novel = types.InlineKeyboardButton(text="роман", callback_data="novel")
category_thriller = types.InlineKeyboardButton(text="триллер", callback_data="thriller")
category_detective = types.InlineKeyboardButton(text="детектив", callback_data="detective")
cat_keyboard = types.InlineKeyboardMarkup()
cat_keyboard.add(category_adventures, category_detective, category_fantasy, category_novel, category_thriller).add(close_button)

# клавиатура для прохода по категории товара
categories_back = types.InlineKeyboardButton(text="назад", callback_data="cat-back")
categories_next = types.InlineKeyboardButton(text="вперед", callback_data="cat-next")
categories_favorite = types.InlineKeyboardButton(text='\u2605', callback_data='cat-favorite')
categories_del_favorite = types.InlineKeyboardButton(text='\u2605 \u2326', callback_data='cat-del-favorite')
piligrim_keyboard_1 = types.InlineKeyboardMarkup()
piligrim_keyboard_2 = types.InlineKeyboardMarkup()
piligrim_keyboard_1.add(categories_back, categories_next).add(categories_favorite).add(close_button)
piligrim_keyboard_2.add(categories_back, categories_next).add(categories_del_favorite).add(close_button)


welcome_keyboard = types.InlineKeyboardMarkup()
product_button = types.InlineKeyboardButton(text="товар", callback_data="product")
categories_button = types.InlineKeyboardButton(text="категория", callback_data="categories")
welcome_keyboard.add(product_button, categories_button).add(close_button)
# ___________________________________________________________________________


@bot.message_handler(commands=["start"])
def start_chat(message):
    DEL_MESSEGE_ID.append(message.message_id), DEL_MESSEGE_ID.append(message.message_id + 1)
    print(1,DEL_MESSEGE_ID)
    bot.send_message(message.from_user.id, ' Меню', reply_markup=welcome_keyboard)
    # bot.send_message(message.from_user.id, message, reply_markup=welcome_keyboard)


#@bot.message_handler(commands=["delete"])
@bot.callback_query_handler(func=lambda callback: callback.data == 'close')
def start_chat(callback):
    STATE_DICT["list_products"] = None
    CATEGORIES_DICT["genre"] = None
    DEL_MESSEGE_ID.append(callback.message.message_id)
    [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    DEL_MESSEGE_ID.clear()
    # bot.send_message(message.from_user.id, 'удалено')


#@bot.message_handler(commands=["categories"])
@bot.callback_query_handler(func=lambda callback: callback.data == 'categories')
def get_product_categories(callback):
    categories_novel = Product.query.filter_by(genre="Роман", is_published=True).all()
    categories_adventures = Product.query.filter_by(genre="Приключения", is_published=True).all()
    categories_fantasy = Product.query.filter_by(genre="Фэнтези", is_published=True).all()
    categories_thriller = Product.query.filter_by(genre="Триллер", is_published=True).all()
    categories_detective = Product.query.filter_by(genre="Детектив", is_published=True).all()
    DEL_MESSEGE_ID.append(callback.message.message_id + 1), DEL_MESSEGE_ID.append(callback.message.message_id)
    bot.send_message(
        callback.message.chat.id,
        f"<b>Категория</b>\n Роман {len(categories_novel)} шт \n Приключения {len(categories_adventures)} шт \n Фэнтези {len(categories_fantasy)} шт \n Триллер {len(categories_thriller)} шт \n Детектив {len(categories_detective)} шт \n",
        parse_mode="HTML",
        reply_markup=cat_keyboard,
    )


@bot.callback_query_handler(func=lambda callback: callback.data in ['adventures', 'novel', 'fantasy', 'thriller','detective'])
def get_genre_adventures(callback):
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
        images = [i.image for i in current_product.image]
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
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_1
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_2
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
        reply_markup=reply_markup,
    )


@bot.callback_query_handler(func=lambda callback: callback.data == 'cat-del-favorite')
def del_favorite(callback):
    '''
    Удаление товара из списка избранного.
    '''
    list_products = CATEGORIES_DICT["genre"]
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        reply_markup = piligrim_keyboard_1
    elif len(check) == 0:
        reply_markup = piligrim_keyboard_2
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
        reply_markup=reply_markup,
    )

# __________________________________________________________________________________________________________________


#@bot.message_handler(commands=["product"])
@bot.callback_query_handler(func=lambda callback: callback.data == 'product')
def get_product(callback):
    list_products = deque(Product.query.filter_by(is_published=True).all())
    STATE_DICT.clear()
    STATE_DICT["list_products"] = list_products
    current_product = list_products[0]
    check = FavoritesProducts.query.filter_by(user=callback.from_user.id,id_product=current_product.id).all()
    if len(check) > 0:
        markup_product = markup_product_1
    elif len(check) == 0:
        markup_product = markup_product_2
    print(2,DEL_MESSEGE_ID)
    # [bot.delete_message(callback.message.chat.id, id) for id in DEL_MESSEGE_ID]
    # DEL_MESSEGE_ID.clear()
    images = [i.image for i in current_product.image]
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
    ),DEL_MESSEGE_ID.append(callback.message.message_id)


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
    print(3,DEL_MESSEGE_ID)
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


# @app.route('/', methods=['POST'])
# def get_test():
#     data = request.get_json()
#     print (data)
#     return ("ok")


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

