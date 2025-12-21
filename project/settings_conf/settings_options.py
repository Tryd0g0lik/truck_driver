import os

from project.settings_conf.settings_env import *
from project.settings_conf.settings_security import CORS_ALLOWED_ORIGINS

# '''WEBPACK_LOADER'''
WEBPACK_LOADER = {
    "DEFAULT": {
        "CACHE": not DEBUG,
        # 'BUNDLE_DIR_NAME': '..\\frontend\\src\\bundles',
        "BUNDLE_DIR_NAME": "static",
        "STATS_FILE": os.path.join(BASE_DIR, "bundles/webpack-stats.json"),
        "POLL_INTERVAL": 0.1,
        "TIMEOUT": None,
        "TEST": {
            "NAME": "test_cloud",
        },
        "IGNORE": [
            # '.+\.map$'
            r".+\.hot-update.js",
            r".+\.map",
        ],
        "LOADER_CLASS": "webpack_loader.loader.WebpackLoader",
    }
}

# '''lOGGING'''
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# """SWAGGER"""
# https://drf-yasg.readthedocs.io/en/stable/security.html#security-definitions

SWAGGER_USE_COMPAT_RENDERERS = False
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "VALIDATOR_URL": None,
    "exclude_namespaces": [],
}
SPECTACULAR_SETTINGS = {
    "TITLE": "Your API",
    "DESCRIPTION": "Your project description",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
