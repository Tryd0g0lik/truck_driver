"""
project/urls_api.py
"""

from django.urls import path, include
from person.urls_api import router as person_router

urlpatterns = [
    path("auth/", include(person_router.urls), name="auth_api"),
]
