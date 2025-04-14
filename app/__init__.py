"""Flask application factory with configuration and extensions initialization."""

from datetime import datetime

from flask import Flask, make_response, render_template, request, session
from flask_babel import Babel
from flask_babel import gettext as _
from flask_cors import CORS
from flask_minify import Minify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from html_sanitizer import Sanitizer
from werkzeug.middleware.proxy_fix import ProxyFix

from api.v1.views import bp as api_blueprint
from app.extensions import (
    db,
    get_file_url,
    get_locale,
    init_cache,
    init_session,
    migrate,
)
from config import Config
from utils.rate_limiter import init_limiter
from utils.toast_notify import add_toast


def create_sanitizer():
    """Create and configure HTML sanitizer."""
    return Sanitizer(
        {
            "tags": {
                "img",
                "b",
                "i",
                "u",
                "em",
                "strong",
                "a",
                "p",
                "ul",
                "li",
                "br",
                "div",
                "span",
            },
            "attributes": {"a": ("href", "title"), "img": ("src", "alt")},
            "empty": {"a", "br"},  # Tags that can be self-closing
        }
    )


def register_extensions(app):
    """Register Flask extensions with the application."""
    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models to create tables
    from app.models import (
        Contact,
        Course,
        CourseMember,
        Member,
        News,
        Podcast,
        PodcastMember,
        Project,
        Research,
        Subscriber,
        Team,
        User,
    )

    # i18n
    Babel(app, locale_selector=get_locale)

    # Session and caching
    init_session(app)
    init_cache(app)

    # Security
    CSRFProtect(app)
    init_limiter(app)

    # Performance
    Minify(app=app, html=True, js=True, cssless=True)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(api_blueprint)


def configure_cors(app):
    """Configure CORS for the application."""
    CORS(
        app,
        origins=Config.BASE_URL,
        methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
        supports_credentials=True,
        max_age=3600,
    )


def register_template_filters(app, sanitizer):
    """Register custom template filters."""

    @app.template_filter("truncate_html")
    def truncate_html_filter(html_content, length=200):
        """Truncate HTML content while maintaining valid structure."""
        truncated = sanitizer.sanitize(html_content[:length])
        return (
            truncated + "..." if len(html_content) >= length else html_content
        )

    @app.template_filter("file_url")
    def file_url_filter(file_path):
        """Convert stored file paths to public URLs."""
        return get_file_url(file_path)


def register_context_processors(app):
    """Register template context processors."""

    @app.context_processor
    def inject_locale():
        """Inject the locale into each rendered template."""
        lang = request.args.get("lang")
        if lang and lang in Config.BABEL_SUPPORTED_LOCALES:
            session["lang"] = lang
            return {"locale": lang}
        return {"locale": get_locale()}

    @app.context_processor
    def inject_csrf_token():
        """Inject CSRF token into templates."""
        return {"csrf_token": generate_csrf}

    @app.context_processor
    def inject_current_year():
        """Inject current year into templates."""
        return {"current_year": datetime.now().year}


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def page_not_found(_):
        """Handle 404 errors."""
        is_authenticated = "user" in session
        return (
            render_template(
                "not_found.html", is_authenticated=is_authenticated
            ),
            404,
        )

    @app.errorhandler(429)
    def rate_limit_exceeded(_):
        """Handle rate limit errors."""
        return add_toast(
            make_response("", 429), "error", _("Rate limit exceeded")
        )


def register_after_request(app):
    """Register after request handlers."""

    @app.after_request
    def set_security_headers(response):
        """Set security headers for all responses."""
        response.headers["X-Frame-Options"] = "DENY"  # Prevent clickjacking
        return response


def create_app(config_class=Config):
    """Create and configure the Flask application.

    Args:
        config_class: The configuration class to use (defaults to Config)

    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_class)

    # Proxy configuration
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_proto=1, x_host=1, x_port=1, x_prefix=1
    )

    # Initialize extensions
    register_extensions(app)

    # Register blueprints
    register_blueprints(app)

    # Configure CORS
    configure_cors(app)

    # Create sanitizer
    sanitizer = create_sanitizer()

    # Register template filters
    register_template_filters(app, sanitizer)

    # Register context processors
    register_context_processors(app)

    # Register error handlers
    register_error_handlers(app)

    # Register after request handlers
    register_after_request(app)

    # Configure URL map
    app.url_map.strict_slashes = False

    return app
