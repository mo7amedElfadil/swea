"""Various extensions for the Flask application.
like database connections, session, caching, etc.
"""

from flask import session as flask_session
from flask_caching import Cache
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Initialize Flask-SQLAlchemy globally
db = SQLAlchemy()

# Initialize Flask-Migrate globally
migrate = Migrate()


# Initialize Flask-Session globally
session = Session()

# Initialize Flask-Caching globally
cache = Cache()

API_KEY = Config.API_KEY


def init_session(app):
    """Initialize Flask-Session with the provided Flask app."""
    session.init_app(app)


def init_cache(app):
    """Initialize Flask-Caching with the provided Flask app."""
    cache.init_app(app)


def get_locale() -> str:
    """Get the best language for the user from the session."""
    lang = flask_session.get("lang", Config.BABEL_DEFAULT_LOCALE)
    return lang
