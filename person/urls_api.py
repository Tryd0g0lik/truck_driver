from django.db import router
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from person.views_api.users_views import UserViews

router = DefaultRouter()
router.register(r"person", UserViews, basename="persons")
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
]
