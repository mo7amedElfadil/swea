"""configuration file for your Flask application.
"""

from os import getenv, path

import redis
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))

load_dotenv()


class Config:
    """Configuration class for the Flask application."""

    # General App configuration
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

    # MongoDB configuration
    MONGO_URI = getenv("MONGO_URI")
    MONGO_DB_NAME = getenv("MONGO_DB_NAME")

    # Flask cache Configuration
    if DEBUG == 1:
        CACHE_TYPE = "null"
    else:
        CACHE_TYPE = "redis"
        CACHE_REDIS_URL = getenv("CACHE_REDIS_URL")
        CACHE_KEY_PREFIX = "swea_"
        CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
