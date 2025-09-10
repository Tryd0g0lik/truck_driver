"""
person/urls_api.py
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from person.views_api.binary_views import BinaryViews
from person.views_api.users_views import UserViews

router = DefaultRouter()
router.register(r"person", UserViews, basename="persons")
router.register("binary", BinaryViews, basename="binaries")

urlpatterns = [
    path("", include(router.urls), name="persons_api"),
    path(
        "person/0/active/",
        UserViews.as_view({"post": "active"}),
        name="person_active",
    ),
    path(
        "person/<str:pk>/inactive/",
        UserViews.as_view({"patch": "inactive"}),
        name="person_inactive",
    ),
    path(
        "person/<str:pk>/",
        UserViews.as_view({"delete": "delete"}),
        name="person_delete",
    ),
    path(
        "binary/str_to_binary/",
        BinaryViews.as_view({"post": "str_to_binary"}),
        name="str_to_binary",
    ),
    path(
        "binary/binary_to_object/",
        BinaryViews.as_view({"post": "binary_to_object"}),
        name="str_to_binary",
    ),
]
