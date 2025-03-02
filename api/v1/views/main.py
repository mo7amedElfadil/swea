from flask import make_response, redirect, render_template, request, session, url_for,  send_from_directory
from flask_babel import gettext as _

from api.v1.views import bp
from app.extensions import get_locale
from app.services.project_service import ProjectService
from app.services.team_service import TeamService
from config import Config
from utils.map_i18n import normailze_i18n
from utils.referrer_modifier import modify_referrer_lang
from utils.view_modifiers import response
from utils.image_processing import ImageProcessing

# Initialize the service with static dummy data
project_service = ProjectService()
team_service = TeamService()
img = ImageProcessing()


@bp.route("/")
@response(template_file="index.html")
def index():
    """home page"""
    return dict()


@bp.route("/projects")
@response(template_file="projects.html")
@normailze_i18n
def projects():
    """projects page"""
    all_projects = ProjectService().get_all_projects()
    # locale must be included in the dict in order to be normalized
    # DONT' use rqeuest.args.get('lang') as it will return None
    print(all_projects)
    return dict(projects=all_projects, locale=get_locale())


@bp.route("/login", methods=["GET", "POST"])
@response(template_file="login.html")
def login():
    """Login page with HTMX"""

    if request.method == "GET":
        return dict()

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
    page = int(request.args.get("page", 1))
    tab_mapper = {
        "team": "partials/dashboard/team.html",
        "projects": "partials/dashboard/projects.html",
        "knowledge-hub": "partials/dashboard/knowledge_hub.html",
        "subscribers": "partials/dashboard/subscribers.html",
        "news": "partials/dashboard/news.html",
    }
    if request.headers.get("hx-tab"):
        # Fetch projects for the 'projects' tab
        if tab_query == "projects":
            all_projects = project_service.get_all_projects(page=page)
            return make_response(
                render_template(
                    "partials/dashboard/projects.html",
                    locale=locale,
                    projects=all_projects,
                    page=page,
                    total_pages=len(all_projects) // 5 + 1,
                )
            )

        # Fetch team members for the 'team' tab
        if tab_query == "team":
            team_members = team_service.get_all_team_members(page=page)
            return make_response(
                render_template(
                    "partials/dashboard/team.html",
                    **team_members,
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
def knowledge_hub():
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


@bp.route("/team")
@response(template_file="team.html")
def team():
    """team page"""
    all_team_members = TeamService().get_all_team_members()
    return dict(**all_team_members)


@bp.route("/set_language")
def set_language():
    """set language"""
    lang = request.args.get("lang")

    if lang and lang in Config.BABEL_SUPPORTED_LOCALES:
        session["lang"] = lang

    return redirect(modify_referrer_lang(request.referrer, lang))


@bp.route("/toast/<toast_type>")
def get_toast(toast_type):
    """Serve a specific toast template"""
    if toast_type not in ["success", "error", "info", "warning"]:
        return "Toast type not found", 404

    return render_template(f"partials/toast/{toast_type}.html")



@bp.route("/upload/<category>/<uuid>", methods=["POST"])
def upload_image(category, uuid):
    """Upload an image and save it to the appropriate category folder"""
    if category not in ["projects", "research", "courses", "podcasts", "news", "team", "users"]:
        return "Invalid category", 400

    if "file" not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files["file"]
    saved_path = img.save_image(file, category, uuid)

    if saved_path:
        return {"message": "Image uploaded successfully", "path": saved_path}

    return {"error": "Invalid file type"}, 400


@bp.route("/uploads/<path:filename>")
def get_image(filename):
    """Retrieve uploaded images"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
