from flask import (
    flash,
    make_response,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.project_service import ProjectService
from config import Config
from utils.view_modifiers import response

# Initialize the service with static dummy data
project_service = ProjectService()


@bp.route("/")
@response(template_file="index.html")
def index():
    """home page"""
    return dict()


@bp.route("/projects")
@response(template_file="projects.html")
def projects():
    """projects page"""
    return dict()


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page with HTMX"""
    # If it's a GET request, render the login page
    if request.method == "GET":
        return render_template("login.html")

    # Handle POST request (login attempt)
    username = request.form.get("username")
    password = request.form.get("password")
    # Dummy validation (replace with real auth logic)
    if not username or not password:
        return make_response(
            "<p class='text-red-500'>Please enter both username and password to login.</p>",
            400,
        )

    if username != "a" or password != "a":
        return make_response(
            "<p class='text-red-500'>Invalid credentials. Please try again.</p>", 400
        )

    # Successful login - Use HX-Redirect header for redirection
    response = make_response()
    response.headers["HX-Redirect"] = url_for("app_views.dashboard")
    return response


@bp.route("/dashboard")
@response(template_file="dashboard.html")
def dashboard():
    """Dashboard page"""
    locale = session.get("lang", Config.BABEL_DEFAULT_LOCALE)
    tab_query = request.args.get("q", "projects")
    tab_mapper = {
        "team": "partials/dashboard/team.html",
        "projects": "partials/dashboard/projects.html",
        "knowledge-hub": "partials/dashboard/knowledge_hub.html",
        "subscribers": "partials/dashboard/subscribers.html",
    }
    if request.headers.get("hx-tab"):
        # Fetch projects for the 'projects' tab
        if tab_query == "projects":
            page = int(request.args.get("page", 1))
            all_projects = project_service.get_all_projects()
            return make_response(
                render_template(
                    "partials/dashboard/projects.html",
                    locale=locale,
                    projects=all_projects,
                    page=page,
                    total_pages=len(all_projects) // 5 + 1,
                )
            )

        return make_response(
            render_template(
                tab_mapper.get(tab_query, "partials/dashboard/projects.html")
            )
        )
    return dict(tab="projects")


@bp.route("/knowledge-hub")
@response(template_file="knowledge-hub.html")
def knowledge_hup():
    """knowledge-hub page"""
    tab_query = request.args.get("q", "research")
    tab_mapper = {
        "research": "partials/research.html",
        "courses": "partials/courses.html",
        "podcasts": "partials/podcasts.html",
    }

    if request.headers.get("hx-tab"):
        return make_response(
            render_template(
                tab_mapper.get(tab_query, "partials/research.html"), data=dict()
            )
        )
    return dict(tab="research")


@bp.route("/set_language")
def set_language():
    """set language"""
    lang = request.args.get("lang")

    if lang and lang in Config.BABEL_SUPPORTED_LOCALES:
        session["lang"] = lang

    return redirect(request.referrer)
