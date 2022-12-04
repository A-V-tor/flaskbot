import os
import os.path

from flask_admin import Admin, AdminIndexView, BaseView, expose, form
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField

from flaskbot import app, db, server

from .bot import current_user
from .other import (
    AdminProfile,
    CurrentDayUsers,
    DashProfile,
    FavoritesProducts,
    Product,
)


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


admin = Admin(
    server,
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
            ("Философия", "Философия"),
        ]
    }
    form_overrides = {"description": TextAreaField}
    form_widget_args = {"description": {"rows": 5, "style": "font-family: monospace;"}}
    create_modal = True
    edit_modal = True
    path = os.path.abspath(os.getcwd() + "/flaskbot/static/image-product")
    form_extra_fields = {"image": form.ImageUploadField("изображение", base_path=path)}

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


class CurrentDayUsersView(ModelView):
    column_list = ["date", "user", "is_premium", "is_bot", "language_code"]
    column_labels = dict(
        date="дата",
        user="пользователь",
        is_premium="Премиум ?",
        is_bot="Бот ?",
        language_code="языковая зона",
    )

    def is_accessible(self):
        try:
            if current_user.admin:
                return True
        except:
            pass


class DashProfileWiev(ModelView):
    column_list = [
        "name",
        "psw",
    ]
    column_labels = dict(name="логин", psw="пароль")

    def is_accessible(self):
        try:
            if current_user.owner:
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
    AdminProfileView(
        AdminProfile,
        db.session,
        name="Администраторы",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-user",
    )
)

admin.add_view(
    DashProfileWiev(
        DashProfile,
        db.session,
        name=" Юзер - аналитики",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-eye-open",
    )
)
admin.add_view(
    ModelView(
        FavoritesProducts,
        db.session,
        name="Избранное",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-bookmark",
    )
)

admin.add_view(
    CurrentDayUsersView(
        CurrentDayUsers,
        db.session,
        name="1 день",
        menu_icon_type="glyph",
        menu_icon_value="glyphicon-pencil",
    )
)
