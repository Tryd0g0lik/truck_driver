from django.urls import path
from person.views import main_views
from person.contribute.controler_activate import user_activate
from project.urls_api import urlpatterns

app_name = "person_app"
urlpatterns = [
    path("", main_views, name="main_views"),
    path("activate/<str:sign>/", user_activate, name="user_activate"),
]
