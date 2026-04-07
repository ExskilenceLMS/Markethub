import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


def _build_mysql_sqlalchemy_uri(*, strict: bool) -> str:
    driver = os.environ.get("DB_DRIVER", "mysql+pymysql").strip()
    port = os.environ.get("DB_PORT", "3306").strip() or "3306"
    password = os.environ.get("DB_PASSWORD", "")
    if password is None:
        password = ""

    host = os.environ.get("DB_HOST")
    user = os.environ.get("DB_USER")
    database = os.environ.get("DB_NAME")

    if strict:
        missing = [
            name
            for name, val in (
                ("DB_HOST", host),
                ("DB_USER", user),
                ("DB_NAME", database),
            )
            if not val or not str(val).strip()
        ]
        if missing:
            raise ValueError(
                "When FLASK_ENV=production, set non-empty values for: "
                + ", ".join(missing)
            )
    else:
        host = (host or "127.0.0.1").strip()
        user = (user if user is not None else "root").strip() or "root"
        database = (database or "markethub_dev").strip()

    safe_user = quote_plus(user, safe="")
    safe_password = quote_plus(password, safe="")
    return f"{driver}://{safe_user}:{safe_password}@{host}:{port}/{database}"


def resolve_sqlalchemy_database_uri() -> str:
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env == "testing":
        return "sqlite:///:memory:"
    return _build_mysql_sqlalchemy_uri(strict=(env == "production"))


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "true").lower() == "true"


class TestingConfig(BaseConfig):
    TESTING = True


_CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return _CONFIG_BY_NAME.get(env, DevelopmentConfig)
