"""configuration file for your Flask application."""
import os
from os import getenv, path

import redis
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))

load_dotenv()


class Config:
    """Configuration class for the Flask application."""

    # Translation configuration
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"
    BABEL_SUPPORTED_LOCALES = ["en", "ar"]
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(basedir, "app/translations")

    # General App configuration
    UPLOAD_FOLDER = getenv(
        "UPLOAD_FOLDER", os.path.join(basedir, "./app/static/uploads/")
    )
    UPLOAD_DIRS = ["projects", "research", "courses", "podcasts", "news",
                   "team", "users"]
    # Create the upload folder if it doesn't exist
    if not path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    for folder in UPLOAD_DIRS:
        os.makedirs(os.path.join(UPLOAD_FOLDER, folder), exist_ok=True)
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    SECRET_KEY = getenv("SECRET_KEY", "you-will-never-guess")
    PREFERRED_URL_SCHEME = getenv("PREFERRED_URL_SCHEME", "https")
    API_KEY = getenv("API_KEY", "you-will-never-guess")
    SECURITY_PASSWORD_SALT = getenv("SECURITY_PASSWORD_SALT", "you-will-never-guess")
    DEBUG = int(getenv("FLASK_DEBUG", 0))
    BASE_URL = getenv("DEV_BASE_URL") if DEBUG == 1 else getenv("PRODUCTION_BASE_URL")

    # Flask session configuration
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url(getenv("SESSION_REDIS_URL"))

    # Redis Database configuration for queue service
    REDIS_URL = getenv("REDIS_URL")
    TOKEN_REDIS_URL = getenv("TOKEN_REDIS_URL")

    # Database configuration (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = getenv(
        "POSTGRES_URL", "postgresql://swea_user:swea_pass@localhost/swea_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask cache Configuration
    if DEBUG == 1:
        CACHE_TYPE = "null"
    else:
        CACHE_TYPE = "redis"
        CACHE_REDIS_URL = getenv("CACHE_REDIS_URL")
        CACHE_KEY_PREFIX = "swea_"
        CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
