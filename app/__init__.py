"""Module that defines `create_app` function to create the Flask app instance"""

from flask import Flask, make_response, render_template, request, send_from_directory
from flask import session
from flask import session as flask_session
from flask_babel import Babel
from flask_babel import gettext as _
from flask_cors import CORS
from flask_minify import Minify
from html_sanitizer import Sanitizer
from werkzeug.middleware.proxy_fix import ProxyFix

from api.v1.views import bp as app_view
from app.extensions import db, get_locale, init_cache, init_session, migrate
from config import Config
from utils.rate_limiter import init_limiter
from utils.toast_notify import add_toast

# Sanitizer configuration (you can customize it as per your needs)
sanitizer = Sanitizer(
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


def create_app(config_class=Config):
    """Creating a Flask Application Factory,
    and initializing the app extensions.
    Args:
        config_class (Config, optional): The configuration class to use(env variables)
    """
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_class)

    # Initialize Flask-SQLAlchemy
    db.init_app(app)

    # Initialize Flask-Migrate
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
        Team,
        User,
    )

    app.url_map.strict_slashes = False
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # Initialize Flask-Babel (i18n)
    babel = Babel(app, locale_selector=get_locale)

    # Initialize Flask-Session
    init_session(app)

    # Initialize Flask-Caching
    init_cache(app)

    # Register blueprints here
    app.register_blueprint(app_view)

    # Enable CORS for only the base URL
    CORS(
        app,
        origins=Config.BASE_URL,
        methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type"],
        supports_credentials=True,
        max_age=3600,
    )

    # initializing minify for html, js and cssless
    Minify(app=app, html=True, js=True, cssless=True)

    # Initialize the rate limiter
    init_limiter(app)

    @app.context_processor
    def inject_locale():
        """Inject the locale into each rendered template"""
        lang = request.args.get("lang", None)
        if lang and lang in Config.BABEL_SUPPORTED_LOCALES:
            session["lang"] = lang
            return dict(locale=lang)
        return dict(locale=get_locale())

    @app.route("/robots.txt")
    def static_from_root():
        return send_from_directory(app.static_folder, request.path[1:])

    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        is_authenticated = False
        if "user" in flask_session:
            is_authenticated = True

        return render_template("not_found.html", is_authenticated=is_authenticated), 404

    @app.template_filter("truncate_html")
    def truncate_html_filter(html_content, length=200):
        # Clean the HTML content while maintaining valid structure
        truncated = sanitizer.sanitize(html_content[:length])

        # Ensure we add ellipsis only if content is actually truncated
        return truncated + "..." if len(html_content) >= length else html_content

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        """Handle rate limit errors"""
        return add_toast(make_response("", 429), "error", _("Rate limit exceeded"))

    return app
