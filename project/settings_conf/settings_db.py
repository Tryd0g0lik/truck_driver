import logging

from logs import configure_logging
from project.settings_conf.settings_env import *

configure_logging(logging.INFO)
log = logging.getLogger(__name__)

# SECURITY WARNING: don't run with debug turned on in production!

print(f"DEBUG: {DEBUG}, DJANGO_ENV: {DJANGO_ENV}")
# """" HOST """"
def get_allowed_hosts(allowed_hosts: str):
    """
    The function is for the securite connection to the allowed hosts
    """
    from django.core.exceptions import ImproperlyConfigured

    hosts = allowed_hosts.split(", ")
    hosts = [h.strip() for h in hosts if h.strip()]

    if DJANGO_ENV == "production":
        hosts += [
            f"{APP_HOST}",
            "172.19.0.2",
            "db",
            "backend",
            "nginx",
            "celery",
            "redis",
            "[::1]",
        ]

    if not hosts and DJANGO_ENV == "production":
        text_e = "[%s]: ALLOWED_HOSTS must be set in production" % get_allowed_hosts.__name__
        log.error(text_e)
        raise ImproperlyConfigured(text_e)
    return hosts
# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
ALLOWED_HOSTS = get_allowed_hosts("127.0.0.1, localhost, 0.0.0.0")
try:
    # https://docs.djangoproject.com/en/4.2/ref/settings/#databases
    if DJANGO_ENV == "testing":
        log.info(f"DJANGO_ENV == 'testing'': {DJANGO_ENV == "testing"}")
        # TESTING
        if DEBUG:
            DATABASES = {
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": BASE_DIR / "test_person_db.sqlite3",
                }
            }
            log.info("DB: run 'test_person_db.sqlite3'")
        elif not DEBUG and DJANGO_ENV == "testing":
            DATABASES = {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": os.getenv("POSTGRES_DB", "test_myapp_db"),
                    "USER": os.getenv("POSTGRES_USER", "test_user"),
                    "PASSWORD": os.getenv("POSTGRES_PASSWORD", "test_password"),
                    "HOST": f"{POSTGRES_HOST}",
                    "PORT": f"{POSTGRES_PORT}",
                    "KEY_PREFIX": "drive_test_",  # it's my prefix for the keys
                }
            }
            log.info("DB: run the postgres 'test_person_db.sqlite3'")
    elif DEBUG:
        # DEVELOPMENT
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "person_db.sqlite3",
            }
        }
        log.info("DB: run 'person_db.sqlite3'")
    else:

        # PRODUCTION
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": f"{POSTGRES_DB}",
                "USER": f"{POSTGRES_USER}",
                "PASSWORD": f"{POSTGRES_PASSWORD}",
                "HOST": f"{POSTGRES_HOST}",
                "PORT": f"{POSTGRES_PORT}",
                "KEY_PREFIX": "drive_",
                "OPTIONS": {
                    "connect_timeout": 30,
                }
            }
        }
        log.info("DB: RUN")
except Exception as e:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "fallback.db",
        }
    }
