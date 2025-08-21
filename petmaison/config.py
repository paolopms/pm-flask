import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    TIME_ZONE = os.getenv("TIME_ZONE", "America/Santiago")
    MEDIA_ROOT = os.getenv("MEDIA_ROOT", os.path.abspath(os.path.join(os.getcwd(), "media")))
    STATIC_ROOT = os.getenv("STATIC_ROOT", os.path.abspath(os.path.join(os.getcwd(), "static")))
    WTF_CSRF_TIME_LIMIT = None
    # API Docs (Flask-Smorest)
    API_TITLE = "PetMaison API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/api"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLITE_URL",
        f"sqlite:///{os.path.abspath(os.path.join(os.getcwd(), 'instance', 'dev.db'))}",
    )


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")


def get_config() -> type[BaseConfig]:
    env = os.getenv("FLASK_ENV", "production")
    if env == "development":
        return DevelopmentConfig
    return ProductionConfig
