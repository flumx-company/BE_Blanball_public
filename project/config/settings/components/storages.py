from os import environ
from typing import Any

from decouple import config

if environ.get("GITHUB_WORKFLOW"):
    DATABASES: dict[str, Any] = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": "postgres_test",
            "USER": "postgres_test",
            "PASSWORD": "postgres_test",
            "HOST": "127.0.0.1",
            "PORT": 5432,
        }
    }
    CHANNEL_LAYERS: dict[str, Any] = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", config("REDIS_PORT", cast=int))],
            },
        },
    }
else:
    DATABASES: dict[str, Any] = {
        "default": {
            "ENGINE": config("DB_ENGINE", cast=str),
            "NAME": config("POSTGRES_DB", cast=str),
            "USER": config("POSTGRES_USER", cast=str),
            "PASSWORD": config("POSTGRES_PASSWORD", cast=str),
            "HOST": config("POSTGRES_HOST", cast=str),
            "PORT": config("POSTGRES_PORT", cast=int),
        }
    }
    CHANNEL_LAYERS: dict[str, Any] = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("redis", config("REDIS_PORT", cast=int))],
            },
        },
    }

if not environ.get("GITHUB_WORKFLOW"):
    MINIO_ENDPOINT: str = config("FILE_STORAGE_ENDPOINT", cast=str)
    DEFAULT_FILE_STORAGE: str = config("FILE_STORAGE", cast=str)
    MINIO_MEDIA_FILES_BUCKET: str = config("FILE_STORAGE_MEDIA_BUCKET_NAME", cast=str)
    MINIO_USE_HTTPS: bool = config("FILE_STORAGE_USE_HTTPS", cast=bool)
    MINIO_CONSISTENCY_CHECK_ON_START: bool = True
    MINIO_BUCKET_CHECK_ON_SAVE: bool = True
    MINIO_ACCESS_KEY: str = config("MINIO_ROOT_USER", cast=str)
    MINIO_SECRET_KEY: str = config("MINIO_ROOT_PASSWORD", cast=str)
    MINIO_PUBLIC_BUCKETS: list[str] = []
    MINIO_PUBLIC_BUCKETS.append(MINIO_MEDIA_FILES_BUCKET)
