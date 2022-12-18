import datetime

from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from telebot import types

from flaskbot import db


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.datetime.now)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    quntility = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    price = db.Column(db.Integer)
    image = db.Column(db.String(100), nullable=False)
    is_published = db.Column(db.Boolean)
    favorites = relationship("FavoritesProducts", backref="product", lazy=True)

    def __str__(self):
        return self.name


class AdminProfile(db.Model, UserMixin):
    __tablename__ = "adminprofile"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))
    tg_id = db.Column(db.String(100), nullable=True)
    admin = db.Column(db.Boolean, nullable=False, default=True)
    owner = db.Column(db.Boolean, nullable=False, default=False)

    def __str__(self):
        return self.name


class DashProfile(db.Model):
    __tablename__ = "dashprofile"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))


class FavoritesProducts(db.Model):
    __tablename__ = "favoritesproducts"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    name = db.Column(db.String(100))
    id_product = db.Column(db.Integer, ForeignKey("product.id"))

    def __str__(self):
        return self.name


class CurrentUsers(db.Model):
    """
    Модель юзеров текущего дня.
    """

    __tablename__ = "current_users"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.datetime.now)
    user = db.Column(db.String(100))
    is_premium = db.Column(db.Boolean, nullable=False, default=None)
    is_bot = db.Column(db.Boolean, nullable=False, default=False)
    language_code = db.Column(db.String(10), default="ru")


class InfoMessage(db.Model):
    __tablename__ = "info_message"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.datetime.now)
    text = db.Column(db.String(700))
    is_published = db.Column(db.Boolean, default=False)


db.create_all()

# admin_user = AdminProfile(name='admin', psw='admin', owner=True)
# db.session.add(admin_user)
# db.session.commit()

# ____________________________________КЛАВИАТУРЫ________________________


""" welcome_keyboard """
welcome_keyboard = types.InlineKeyboardMarkup()
product_button = types.InlineKeyboardButton(text="🎁", callback_data="product")
categories_button = types.InlineKeyboardButton(text="🚥", callback_data="categories")
close_button_start = types.InlineKeyboardButton(text="❌", callback_data="close-start")
get_favorites = types.InlineKeyboardButton(text="✨✨✨", callback_data="get-favorites")
welcome_keyboard.add(product_button, categories_button, get_favorites).add(
    close_button_start
)

""" закрытие вкладки товар """
close_button = types.InlineKeyboardButton(text="❌", callback_data="close")

""" кнопки для прохода по списку товаров """
inline_back = types.InlineKeyboardButton(text="◀", callback_data="back")
inline_next = types.InlineKeyboardButton(text="▶", callback_data="next")
inline_favorite = types.InlineKeyboardButton(text="💾", callback_data="favorite")
inline_del_favorite = types.InlineKeyboardButton(
    text=" ⭐ ", callback_data="delfavorite"
)
inline_pay = types.InlineKeyboardButton(text="💵", callback_data="pay")

# клавиатура товара с "добавить в избраное"
markup_product_1 = types.InlineKeyboardMarkup()
markup_product_1.add(inline_back, inline_next).add(inline_del_favorite, inline_pay).add(
    close_button
)
# клавиатура товара с "убрать из избраное"
markup_product_2 = types.InlineKeyboardMarkup()
markup_product_2.add(inline_back, inline_next).add(inline_favorite, inline_pay).add(
    close_button
)
# _____________________________________________________________________________


close_button_categories = types.InlineKeyboardButton(
    text="❌", callback_data="close-categories"
)
# клавиатура показа категорий товара

category_adventures = types.InlineKeyboardButton(
    text="приключения", callback_data="adventures"
)
category_fantasy = types.InlineKeyboardButton(text="фентези", callback_data="fantasy")
category_novel = types.InlineKeyboardButton(text="роман", callback_data="novel")
category_thriller = types.InlineKeyboardButton(text="триллер", callback_data="thriller")
category_philosophy = types.InlineKeyboardButton(
    text="философия", callback_data="philosophy"
)
category_detective = types.InlineKeyboardButton(
    text="детектив", callback_data="detective"
)
cat_keyboard = types.InlineKeyboardMarkup()
cat_keyboard.add(
    category_adventures,
    category_detective,
    category_fantasy,
    category_novel,
    category_thriller,
    category_philosophy,
).add(close_button_categories)

# клавиатура для прохода по категории товара
categories_back = types.InlineKeyboardButton(text="◀", callback_data="cat-back")
categories_next = types.InlineKeyboardButton(text="▶", callback_data="cat-next")
categories_favorite = types.InlineKeyboardButton(text="💾", callback_data="cat-favorite")
categories_del_favorite = types.InlineKeyboardButton(
    text=" ⭐ ", callback_data="cat-del-favorite"
)
piligrim_pay = types.InlineKeyboardButton(text="💵", callback_data="piligrim-pay")
piligrim_keyboard = types.InlineKeyboardMarkup()
piligrim_keyboard_1 = types.InlineKeyboardMarkup()
piligrim_keyboard_2 = types.InlineKeyboardMarkup()
piligrim_keyboard_1.add(categories_back, categories_next).add(
    categories_favorite, piligrim_pay
).add(close_button)
piligrim_keyboard_2.add(categories_back, categories_next).add(
    categories_del_favorite, piligrim_pay
).add(close_button)
piligrim_keyboard.add(categories_back, categories_next)

# клавиатура для прохода по списку избранного
favorites_keyboard = types.InlineKeyboardMarkup()
favorites_next = types.InlineKeyboardButton(text="▶", callback_data="fav-next")
favorites_back = types.InlineKeyboardButton(text="◀", callback_data="fav-back")
favorites_del = types.InlineKeyboardButton(text="⭐", callback_data="fav-del")
favorites_keyboard.add(favorites_back, favorites_next).add(favorites_del, close_button)

# клавиатура для прохода по списку поиска

search_keyboard_1 = types.InlineKeyboardMarkup()
search_keyboard_2 = types.InlineKeyboardMarkup()
search_keyboard = types.InlineKeyboardMarkup()
search_next = types.InlineKeyboardButton(text="▶", callback_data="search-next")
search_back = types.InlineKeyboardButton(text="◀", callback_data="search-back")
search_favorite = types.InlineKeyboardButton(text="💾", callback_data="search-favorite")
search_del_favorite = types.InlineKeyboardButton(
    text="⭐", callback_data="search-del-favorite"
)
search_pay = types.InlineKeyboardButton(text="💵", callback_data="search-pay")
search_keyboard_1.add(search_back, search_next).add(
    search_del_favorite, search_pay
).add(close_button)
search_keyboard_2.add(search_back, search_next).add(search_favorite, search_pay).add(
    close_button
)
search_keyboard.add(search_back, search_next)


def arbeit_func():
    pass
