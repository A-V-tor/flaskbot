import os.path

from flask_admin import Admin, AdminIndexView, BaseView, expose, form
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField

from flaskbot import app, db

from .other import Image, Product


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            return True
        except:
            pass


admin = Admin(
    app,
    name="",
    template_mode="bootstrap3",
    index_view=MyAdminIndexView(
        name="Админка", menu_icon_type="glyph", menu_icon_value="glyphicon-home"
    ),
)


class ImageView(ModelView):
    column_display_pk = True
    can_view_details = True
    column_hide_backrefs = False
    column_editable_list = ["image"]
    column_list = ["id", "image", "product_id"]
    column_default_sort = "image"
    column_descriptions = dict(image="хранятся в /image-product/")
    column_labels = dict(image="изображение", product_id="идентификатор товара")
    create_modal = True
    edit_modal = True
    path = os.path.join(os.path.dirname(__file__), "static/image-product")
    form_extra_fields = {"image": form.ImageUploadField("изображение", base_path=path)}


class ProductView(ModelView):
    column_display_pk = True
    can_view_details = True
    column_list = [
        "id",
        "date",
        "name",
        "description",
        "quntility",
        "genre",
        "price",
        "is_published",
        "image",
    ]
    column_sortable_list = [
        "date",
        "name",
        "quntility",
        "genre",
        "price",
        "is_published",
    ]
    column_filters = ["price", "name", "quntility", "genre", "price", "is_published"]
    column_editable_list = ["is_published"]
    column_descriptions = dict(image="хранятся в /image-product/")
    column_labels = dict(
        date="дати и время",
        name="товар",
        description="описание",
        quntility="кол-во",
        genre="жанр",
        price="цена",
        is_published="опубликован ?",
        image="изображение",
    )

    form_choices = {
        "genre": [
            ("Приключения", "Приключения"),
            ("Фэнтези", "Фэнтези"),
            ("Роман", "Роман"),
            ("Триллер", "Триллер"),
            ("Детектив", "Детектив"),
        ]
    }
    form_overrides = {"description": TextAreaField}
    form_widget_args = {"description": {"rows": 5, "style": "font-family: monospace;"}}
    create_modal = True
    edit_modal = True


path = os.path.join(os.path.dirname(__file__), "static")
admin.add_view(
    FileAdmin(
        path,
        "/static/",
        name="Загрузка файлов",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-circle-arrow-down",
    )
)

admin.add_view(ProductView(Product, db.session, name="Товары"))
admin.add_view(ImageView(Image, db.session, name="Фото"))
