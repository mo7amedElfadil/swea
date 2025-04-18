"""Module instantiates Blueprint for all the views"""

from flask import (
    Blueprint,
    Response,
    make_response,
    redirect,
    request,
    session,
    url_for,
)
from flask_babel import gettext as _

from app.extensions import generate_robots_txt, generate_sitemap_xml
from utils.toast_notify import add_toast

bp = Blueprint("app_views", __name__, template_folder="templates")

from api.v1.views.knowledge_hub import *
from api.v1.views.main import *
from api.v1.views.news import *
from api.v1.views.projects import *
from api.v1.views.subscribers import *
from api.v1.views.team import *

# Define important public routes to include in sitemap
PUBLIC_ROUTES = [
    ("/", "daily", 1.0),
    ("/news", "daily", 0.9),
    ("/projects", "weekly", 0.8),
    ("/team", "monthly", 0.7),
    ("/knowledge-hub", "weekly", 0.8),
    ("/subscribe", "yearly", 0.5),
    ("/unsubscribe", "yearly", 0.5),
    ("/contact-us", "monthly", 0.6),
]


@bp.route("/sitemap.xml")
def sitemap():
    """Route to serve sitemap.xml"""
    sitemap_xml = generate_sitemap_xml(PUBLIC_ROUTES)
    return Response(sitemap_xml, mimetype="application/xml")


@bp.route("/robots.txt")
def robots_txt():
    """Serve the robots.txt file."""
    robots_content = generate_robots_txt()
    return Response(robots_content, mimetype="text/plain")


@bp.before_request
def restrict_dashboard():
    """Restrict access to dashboard routes if not logged in."""
    if request.path.startswith("/dashboard") and "user" not in session:
        if request.headers.get("HX-Request") == "true":
            response = make_response()
            response.headers["HX-Redirect"] = url_for("app_views.login")
            return add_toast(
                response, "error", _("Please log in to access this page")
            )
        else:
            return redirect(url_for("app_views.login"))
