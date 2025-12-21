import logging
from datetime import timedelta

from logs import configure_logging
from project.settings_conf.settings_env import *

configure_logging(logging.INFO)
log = logging.getLogger(__name__)
# '''CORS'''
# False - this value is default and it's means what the server don't accept from other sources.
CORS_ORIGIN_ALLOW_ALL = False
# Here, we allow the URL list for publicated
CORS_ALLOWED_ORIGINS = [

    "http://127.0.0.1:8080",
    "http://localhost:8080",

]

# https://github.com/adamchainz/django-cors-headers?tab=readme-ov-file#csrf-integration
# https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-CSRF_TRUSTED_ORIGINS
# This is list from private of URL
CSRF_TRUSTED_ORIGINS = [*CORS_ALLOWED_ORIGINS]
# Allow the cookie in HTTP request.
CORS_ALLOW_CREDENTIALS = True
# Allow the methods to the methods in HTTP
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "Authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "Accept-Language",
    "Content-Language",
]

# PASSWORD_RESET_TIMEOUT_DAYS = 1
# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

# """REST_FRAMEWORK SETTINGS AND JWT-tokens"""
# https://pypi.org/project/djangorestframework-simplejwt/4.3.0/
# https://django-rest-framework-simplejwt.readthedocs.io/en/latest/stateless_user_authentication.html
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # This for works with sessions
        "rest_framework.authentication.TokenAuthentication",  # Options for API
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(JWT_ACCESS_TOKEN_LIFETIME_MINUTES)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(JWT_REFRESH_TOKEN_LIFETIME_DAYS)),
    "SIGNING_KEY": f"{SECRET_KEY_DJ}",
}
