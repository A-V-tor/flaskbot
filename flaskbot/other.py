import datetime

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
    image = relationship("Image", backref="product")
    favorites = relationship("FavoritesProducts", backref="product")


class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey("product.id"))
    image = db.Column(db.String(100))  # переименовать на name_image


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


db.create_all()
