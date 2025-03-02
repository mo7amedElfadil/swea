from flask import make_response, redirect, render_template, request, session, url_for
from flask_babel import gettext as _

from api.v1.views import bp
from app.extensions import get_locale
from app.services.news import NewsService
from app.services.project_service import ProjectService
from app.services.team_service import TeamService
from config import Config
from utils.map_i18n import normailze_i18n
from utils.referrer_modifier import modify_referrer_lang
from utils.view_modifiers import response


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
    projects = ProjectService().get_all_projects()
    # locale must be included in the dict in order to be normalized
    # DONT' use rqeuest.args.get('lang') as it will return None
    return dict(**projects, locale=get_locale())


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
    tab_query = request.args.get("q")
    if tab_query is None:
      return dict(tab="projects")

    tab_content = dict(
        team=dict(temp="partials/dashboard/team.html",
                  data=TeamService().get_all),
        projects=dict(temp="partials/dashboard/projects.html",
                      data=ProjectService().get_all_projects),
        knowledge_hub=dict(temp="partials/dashboard/knowledge-hub.html",
                           data=dict),
        subscribers=dict(temp="partials/dashboard/subscribers.html",
                         data=dict),
        news=dict(temp="partials/dashboard/news.html",
                  data=NewsService().get_all),
        )
    template = tab_content.get(tab_query, {}).get("temp")
    data = tab_content.get(tab_query, {}).get("data", lambda: {})()
    print('=======>',data)

    return make_response(render_template(
      template,
      **data,
    ))
                                             
        
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


@bp.route("/team")
@response(template_file="team.html")
def team():
    """team page"""
    all_team_members = TeamService().get_all()
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
