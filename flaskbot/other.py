import datetime

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


class Image(db.Model):
    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, ForeignKey("product.id"))
    image = db.Column(db.String(100))  # переименовать на name_image


db.create_all()
