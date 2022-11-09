from decouple import config

EMAIL_BACKEND: str = config("EMAIL_BACKEND", cast=str)
EMAIL_HOST: str = config("EMAIL_HOST", cast=str)
EMAIL_PORT: int = config("EMAIL_PORT", cast=int)
EMAIL_USE_TLS: bool = config("EMAIL_USE_TLS", cast=bool)
EMAIL_HOST_USER: str = config("EMAIL_HOST_USER", cast=str)
EMAIL_HOST_PASSWORD: str = config("EMAIL_HOST_PASSWORD", cast=str)
