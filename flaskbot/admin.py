import os.path

from flask_admin import Admin, AdminIndexView, BaseView, expose, form
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
# from wtforms.fields import SelectField, BooleanField
from wtforms import TextAreaField

from flaskbot import app, db

from .bot import current_user
from .other import AdminProfile, Image, Product, FavoritesProducts


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


admin = Admin(
    app,
    name="",
    template_mode="bootstrap3",
    index_view=MyAdminIndexView(
        name="Админка", menu_icon_type="glyph", menu_icon_value="glyphicon-send"
    ),
)


class AnalyticsView(BaseView):
    @expose("/")
    def index(self):
        return self.render(
            "admin/analytics_index.html",
        )

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


class AdminProfileView(ModelView):
    can_view_details = True
    column_editable_list = ["admin"]
    column_default_sort = "name"
    column_descriptions = dict(
        owner="могут создавать новых пользоавтелей и раздавать права"
    )
    create_modal = True
    edit_modal = True
    column_labels = dict(
        name="Логин",
        psw="Пароль",
        admin="Права админа",
        owner="Права владельца",
    )

    def is_accessible(self):
        try:
            if current_user.owner:
                return True
        except:
            pass


class ImageView(ModelView):
    column_display_pk = True
    can_view_details = True
    column_hide_backrefs = False
    column_editable_list = ["name"]
    column_list = ["id", "name", "product_id", "product.name"]
    column_default_sort = "name"
    column_descriptions = dict(image="хранятся в /image-product/")
    column_labels = dict(image="изображение", product_id="идентификатор товара")
    create_modal = True
    edit_modal = True
    path = os.path.join(os.path.dirname(__file__), "static/image-product")
    form_extra_fields = {"name": form.ImageUploadField("изображение", base_path=path)}

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


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

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


admin.add_view(
    AnalyticsView(
        name="Аналитика",
        endpoint="analytics",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-stats",
    )
)


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

admin.add_view(
    ProductView(
        Product,
        db.session,
        name="Товары",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-shopping-cart",
    )
)
admin.add_view(
    ImageView(
        Image,
        db.session,
        name="Фото",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-picture",
    )
)
admin.add_view(
    AdminProfileView(
        AdminProfile,
        db.session,
        name="Администраторы",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-user",
    )
)
admin.add_view(ModelView(FavoritesProducts, db.session, name='Избранное'))