from os import path

import django
from decouple import Csv, config
from django.utils.encoding import smart_str

django.utils.encoding.smart_text = smart_str

from django.conf import settings

################################################################

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing: dirname(dirname(dirname(__file__)))

FILE_UPLOAD_MAX_MEMORY_SIZE = 1024

SECRET_KEY: str = config("SECRET_KEY", cast=str)

DEBUG: bool = config("DEBUG", cast=bool)

ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", cast=Csv())
################################################################

STATIC_URL: str = "/api/static/"
STATIC_ROOT: str = path.join(settings._BASE_DIR, "static/")

WSGI_APPLICATION: str = "config.wsgi.application"
ASGI_APPLICATION: str = "config.asgi.application"

ROOT_URLCONF: str = "config.urls"

LANGUAGE_CODE: str = config("LANGUAGE_CODE", cast=str)

TIME_ZONE: str = config("TIME_ZONE", cast=str)
USE_I18N: bool = config("USE_I18N", cast=bool)
USE_TZ: bool = config("USE_TZ", cast=bool)

DEFAULT_AUTO_FIELD: str = "django.db.models.BigAutoField"

PAGINATION_PAGE_SIZE: int = config("PAGINATION_PAGE_SIZE", cast=int)

AUTH_USER_MODEL: str = config("AUTH_USER_MODEL", cast=str)

CODE_EXPIRE_MINUTES_TIME: int = config("CODE_EXPIRE_MINUTES_TIME", cast=int)

ALGORITHM: str = config("ALGORITHM", cast=str)
