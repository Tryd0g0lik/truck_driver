from django.urls import path
from person.views import main_views
from person.contribute.controler_activate import user_activate


app_name = "person_app"
urlpatterns = [
    path("", main_views, name="main_views"),
    path("register/", main_views, name="main_views"),
    path("login/", main_views, name="main_views"),
    path("raport/", main_views, name="main_views"),
]
