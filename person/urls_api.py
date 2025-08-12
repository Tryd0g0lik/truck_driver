from django.db import router
from rest_framework.routers import DefaultRouter
from person.views_api.users_views import UserViews

router = DefaultRouter()
router.register(r"person", UserViews, basename="persons")
