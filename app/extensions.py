"""Various extensions for the Flask application.
like database connections, session, caching, etc.
"""

from pymongo import MongoClient
from flask_caching import Cache
from flask_session import Session
from config import Config


# Initialize PyMongo globally
db = MongoClient(Config.MONGO_URI)['swea']

# Initialize Flask-Session globally
session = Session()

# Initialize Flask-Caching globally
cache = Cache()

API_KEY = Config.API_KEY


def init_session(app):
    """Initialize Flask-Session with the provided Flask app."""
    session.init_app(app)


def get_mongo_uri_options():
    """Get MongoDB URI options."""
    options = [
        "retryWrites=true",
        "w=majority",
        "maxPoolSize=50",
        "minPoolSize=5",
        "maxIdleTimeMS=10000",
        "connectTimeoutMS=2000",
        "socketTimeoutMS=5000",
        "readPreference=primaryPreferred",
    ]
    return "&".join(options)


def init_cache(app):
    """Initialize Flask-Caching with the provided Flask app."""
    cache.init_app(app)
