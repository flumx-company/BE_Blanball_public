import datetime
import os
from typing import Any

from decouple import Csv, config
from django.conf import settings

INSTALLED_APPS: list[str] = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Other libs apps:
    "corsheaders",
    "rest_framework_swagger",
    "rest_framework",
    "django_inlinecss",
    "drf_yasg",
    "django_filters",
    "phonenumber_field",
    "channels",
    "storages",
    # My apps:
    "events.apps.EventsConfig",
    "authentication.apps.AuthenticationConfig",
    "notifications.apps.NotificationsConfig",
    "reviews.apps.ReviewsConfig",
]

if not os.environ.get("GITHUB_WORKFLOW"):
    INSTALLED_APPS.append("django_minio_backend.apps.DjangoMinioBackendConfig")

MIDDLEWARE: list[str] = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "corsheaders.middleware.CorsPostCsrfMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "events.middlewares.RequestMiddleware",
]

AUTH_PASSWORD_VALIDATORS: list[dict[str, str]] = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

TEMPLATES: list[dict[str, Any]] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(settings._BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

SWAGGER_SETTINGS: dict[str, Any] = {
    "SHOW_REQUEST_HEADERS": config("SHOW_REQUEST_HEADERS", cast=bool),
    "HIDE_HOSTNAME": True,
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "Header"}
    },
    "USE_SESSION_AUTH": config("USE_SESSION_AUTH", cast=bool),
    "JSON_EDITOR": config("JSON_EDITOR", cast=bool),
    "SUPPORTED_SUBMIT_METHODS": (
        "get",
        "post",
        "put",
        "delete",
    ),
}


REST_FRAMEWORK: dict[str, Any] = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_RENDERER_CLASSES": ("config.renderers.CustomRenderer",),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_PAGINATION_CLASS": "config.pagination.CustomPagination",
}

SIMPLE_JWT: dict[str, Any] = {
    "AUTH_HEADER_TYPES": (config("AUTH_HEADER_TYPES", cast=str)),
    "ACCESS_TOKEN_LIFETIME": datetime.timedelta(
        days=config("ACCESS_TOKEN_LIFETIME", cast=int)
    ),
    "REFRESH_TOKEN_LIFETIME": datetime.timedelta(
        days=config("REFRESH_TOKEN_LIFETIME", cast=int)
    ),
}


CORS_ALLOWED_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://178.151.201.167:49201",
    "http://localhost:4172",
]

CORS_ALLOW_METHODS: list[str] = [
    "DELETE",
    "GET",
    "OPTIONS",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS: list[str] = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]
