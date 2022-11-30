import datetime

from telebot import types
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from flaskbot import db


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(), default=datetime.datetime.now)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    quntility = db.Column(db.Integer)
    genre = db.Column(db.String(50))
    price = db.Column(db.Integer)
    is_published = db.Column(db.Boolean)
    image = relationship("Image", backref="product", lazy='joined')
    favorites = relationship("FavoritesProducts", backref="product", lazy='joined')

    def __str__(self):
        return self.name


class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey("product.id"))
    name = db.Column(db.String(100))

    def __str__(self):
        return self.name


class AdminProfile(db.Model, UserMixin):
    __tablename__ = "adminprofile"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    psw = db.Column(db.String(300))
    admin = db.Column(db.Boolean, nullable=False, default=True)
    owner = db.Column(db.Boolean, nullable=False, default=False)

    def __str__(self):
        return self.name


class FavoritesProducts(db.Model):
    __tablename__ = "favoritesproducts"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100))
    name = db.Column(db.String(100))
    id_product = db.Column(db.Integer, ForeignKey("product.id"))

    def __str__(self):
        return self.name


db.create_all()


# ____________________________________КЛАВИАТУРЫ________________________


''' welcome_keyboard '''
welcome_keyboard = types.InlineKeyboardMarkup()
product_button = types.InlineKeyboardButton(text="товар", callback_data="product")
categories_button = types.InlineKeyboardButton(text="категория", callback_data="categories")
close_button_start = types.InlineKeyboardButton(text="❌", callback_data="close-start")
get_favorites = types.InlineKeyboardButton(text="✨✨✨", callback_data="get-favorites")
welcome_keyboard.add(product_button, categories_button, get_favorites).add(close_button_start)

''' закрытие вкладки товар '''
close_button = types.InlineKeyboardButton(text="❌", callback_data="close")

''' кнопки для прохода по списку товаров '''
inline_back = types.InlineKeyboardButton(text="назад", callback_data="back")
inline_next = types.InlineKeyboardButton(text="вперед", callback_data="next")
inline_favorite = types.InlineKeyboardButton(text="🌟", callback_data="favorite")
inline_del_favorite = types.InlineKeyboardButton(text=" ⭐ ", callback_data="delfavorite")
inline_pay = types.InlineKeyboardButton(text="Купить", callback_data="pay")

# клавиатура товара с "добавить в избраное"
markup_product_1 = types.InlineKeyboardMarkup()
markup_product_1.add(inline_back, inline_next).add(inline_del_favorite, inline_pay).add(close_button)
# клавиатура товара с "убрать из избраное"
markup_product_2 = types.InlineKeyboardMarkup()
markup_product_2.add(inline_back, inline_next).add(inline_favorite, inline_pay).add(close_button)
# _____________________________________________________________________________


close_button_categories = types.InlineKeyboardButton(text="❌", callback_data="close-categories")
# клавиатура показа категорий товара

category_adventures = types.InlineKeyboardButton(text="приключения", callback_data="adventures")
category_fantasy = types.InlineKeyboardButton(text="фентези", callback_data="fantasy")
category_novel = types.InlineKeyboardButton(text="роман", callback_data="novel")
category_thriller = types.InlineKeyboardButton(text="триллер", callback_data="thriller")
category_detective = types.InlineKeyboardButton(text="детектив", callback_data="detective")
cat_keyboard = types.InlineKeyboardMarkup()
cat_keyboard.add(category_adventures, category_detective, category_fantasy, category_novel, category_thriller).add(close_button_categories)

# клавиатура для прохода по категории товара
categories_back = types.InlineKeyboardButton(text="назад", callback_data="cat-back")
categories_next = types.InlineKeyboardButton(text="вперед", callback_data="cat-next")
categories_favorite = types.InlineKeyboardButton(text='🌟', callback_data='cat-favorite')
categories_del_favorite = types.InlineKeyboardButton(text=' ⭐ ', callback_data='cat-del-favorite')
piligrim_keyboard_1 = types.InlineKeyboardMarkup()
piligrim_keyboard_2 = types.InlineKeyboardMarkup()
piligrim_keyboard_1.add(categories_back, categories_next).add(categories_favorite).add(close_button)
piligrim_keyboard_2.add(categories_back, categories_next).add(categories_del_favorite).add(close_button)

# клавиатура для прохода по списку избранного
favorites_keyboard = types.InlineKeyboardMarkup()
favorites_next = types.InlineKeyboardButton(text="вперед", callback_data="fav-next")
favorites_back = types.InlineKeyboardButton(text="назад", callback_data="fav-back")
favorites_del = types.InlineKeyboardButton(text="⭐", callback_data="fav-del")
favorites_keyboard.add(favorites_back, favorites_next).add(favorites_del, close_button)