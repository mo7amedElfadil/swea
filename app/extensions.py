"""Various extensions for the Flask application.
like database connections, session, caching, etc.
"""

import datetime
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

    with open(Config.DISPOSABLE_EMAIL_FILE, encoding="utf-8") as file:
        for line in file:
            domain = line.strip().lower()
            if domain:
                disposable_domains.add(domain)

    return disposable_domains


# Global set for quick lookup
DISPOSABLE_DOMAINS = load_disposable_domains()


def generate_sitemap_xml(public_routes):
    """Generate sitemap.xml content dynamically."""
    today = datetime.date.today().isoformat()

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    for route, freq, priority in public_routes:
        xml_content += f"""    <url>
        <loc>https://aidluminate.pro{route}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>{freq}</changefreq>
        <priority>{priority}</priority>
    </url>
"""

    xml_content += "</urlset>"
    return xml_content


def generate_robots_txt():
    """Generate a robots.txt file dynamically."""
    return """User-agent: *
Disallow: /dashboard/
Disallow: /dashboard/*
Disallow: /admin/
Disallow: /private/
Allow: /
Sitemap: https://aidluminate.pro/sitemap.xml
"""


def get_file_url(file_path):
    """
    Get the URL for a file path stored in the database.

    This function can be registered with Jinja to easily generate URLs
    for files in templates.

    Args:
        file_path: The file path as stored in the database

    Returns:
        The full URL to access the file
    """
    if not file_path:
        return ""

    if Config.STORAGE_TYPE == "s3":
        if Config.S3_REGION and Config.S3_REGION != "us-east-1":
            return f"https://{Config.S3_BUCKET}.s3.{Config.S3_REGION}.amazonaws.com/{file_path}"
        return f"https://{Config.S3_BUCKET}.s3.amazonaws.com/{file_path}"

    # Local file - use our route
    return f"/uploads/{file_path}"
