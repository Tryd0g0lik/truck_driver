import os
from pathlib import Path

import dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"===BASE_DIR=================== {BASE_DIR} ======================BASE_DIR=====")
dotenv.load_dotenv()
IS_DEBUG = os.getenv("IS_DEBUG", "1")
DEBUG = True if int(IS_DEBUG) == 1 else False
# '''' .ENV ''''
IS_DEBUG = os.getenv("IS_DEBUG", "")
PYTHONPATH = os.getenv("PYTHONPATH", "")
SECRET_KEY_DJ = os.getenv("SECRET_KEY_DJ", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_USER = os.getenv("POSTGRES_USER", "")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "")
DB_ENGINE = os.getenv("DB_ENGINE", "")

APP_PROTOCOL: str = os.getenv("APP_PROTOCOL", "")
APP_HOST: str = os.getenv("APP_HOST", "")
APP_PORT = os.getenv("APP_PORT", "")
APP_TIME_ZONE = os.getenv("APP_TIME_ZONE", "")

JWT_ACCESS_TOKEN_LIFETIME_MINUTES = os.getenv("JWT_ACCESS_TOKEN_LIFETIME_MINUTES", "0")
JWT_REFRESH_TOKEN_LIFETIME_DAYS = os.getenv("JWT_REFRESH_TOKEN_LIFETIME_DAYS", "0")
# db
DATABASE_ENGINE_REMOTE = os.getenv("DATABASE_ENGINE_REMOTE", "")
DATABASE_ENGINE_LOCAL = os.getenv("DATABASE_ENGINE_LOCAL", "")
DATABASE_LOCAL = os.getenv("DATABASE_LOCAL", "")
# Redis
REDIS_LOCATION_URL = os.getenv("REDIS_LOCATION_URL", "")
DB_TO_RADIS_CACHE_USERS = os.getenv("DB_TO_RADIS_CACHE_USERS", "")
DB_TO_RADIS_PORT = os.getenv("DB_TO_RADIS_PORT", "")
DB_TO_RADIS_HOST = os.getenv("DB_TO_RADIS_HOST", "")
REDIS_HOST = os.getenv("REDIS_HOST", "")
# CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")

# Email сервис (опционально)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PORT = os.getenv("SMTP_PORT", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")


URL_REDIRECT_IF_NOTGET_AUTHENTICATION = os.getenv(
    "URL_REDIRECT_IF_NOTGET_AUTHENTICATION", ""
)
URL_REDIRECT_IF_GET_AUTHENTICATION = os.getenv("URL_REDIRECT_IF_GET_AUTHENTICATION", "")
DJANGO_ENV = f'{os.getenv("DJANGO_ENV", "production")}'
