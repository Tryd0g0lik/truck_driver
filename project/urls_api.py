# from person.urls_api import router as person_router
from django.urls import path, include
from person.urls_api import router as person_router
from person.views_api.users_views import UserViews
from project.views import CSRFTokenView

urlpatterns = [
    path("auth/", include(person_router.urls), name="auth_api"),
    path(
        "auth/person/0/active/",
        UserViews.as_view({"post": "active"}),
        name="auth_api_person_active",
    ),
    path("auth/csrftoken/", CSRFTokenView.as_view(), name="token_obtain_pair"),
]
