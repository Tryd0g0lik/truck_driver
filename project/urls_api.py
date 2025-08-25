from django.urls import path, include
from person.urls_api import urlpatterns as person_API_urls

from project.views import CSRFTokenView

urlpatterns = [
    path("auth/", include((person_API_urls, "auth_api"), namespace="auth_api")),
    path("auth/csrftoken/", CSRFTokenView.as_view(), name="token_obtain_pair"),
]
