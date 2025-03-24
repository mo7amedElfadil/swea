"""Various extensions for the Flask application.
like database connections, session, caching, etc.
"""

import os

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


def load_disposable_domains() -> set:
    """Load disposable email domains from a file into a set."""
    disposable_domains = set()
    if not os.path.exists(Config.DISPOSABLE_EMAIL_FILE):
        raise FileNotFoundError(
            f"Disposable email blocklist not found at {Config.DISPOSABLE_EMAIL_FILE}"
        )

    with open(Config.DISPOSABLE_EMAIL_FILE, "r", encoding="utf-8") as file:
        for line in file:
            domain = line.strip().lower()
            if domain:
                disposable_domains.add(domain)

    return disposable_domains


# Global set for quick lookup
DISPOSABLE_DOMAINS = load_disposable_domains()
