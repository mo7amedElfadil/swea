"""Module that defines `create_app` function to create the Flask app instance
"""

from flask import Flask, render_template, request, send_from_directory
from flask import session as flask_session
from flask_cors import CORS
from flask_minify import Minify
from werkzeug.middleware.proxy_fix import ProxyFix

from api.v1.views import bp as app_view
from app.extensions import init_cache, init_session
from config import Config


def create_app(config_class=Config):
    """Creating a Flask Application Factory,
    and initializing the app extensions.
    Args:
        config_class (Config, optional): The configuration class to use(env variables)
    """
    app = Flask(__name__, static_folder="static")
    app.config.from_object(config_class)
    app.url_map.strict_slashes = False
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # Initialize Flask-Session
    init_session(app)

    # Initialize Flask-Caching
    init_cache(app)

    # Register blueprints here
    app.register_blueprint(app_view)

    # Enable CORS for only the base URL
    print('---------->', Config.BASE_URL)
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

    return app

