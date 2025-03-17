from flask import (
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.contact_us import ManageContactUs
from app.services.course_service import CourseService
from app.services.news import NewsService
from app.services.podcast_service import PodcastService
from app.services.project_service import ProjectService
from app.services.research_service import ResearchService
from app.services.subscriber_service import SubscriberService
from app.services.team_service import TeamService
from config import Config
from utils.image_processing import ImageProcessing
from utils.rate_limiter import RateLimits, rate_limit
from utils.referrer_modifier import modify_referrer_lang
from utils.toast_notify import add_toast
from utils.view_modifiers import response

img = ImageProcessing()


@bp.route("/")
@response(template_file="index.html")
def index():
    """home page"""
    page = request.args.get("page", type=int, default=1)
    news = NewsService().get_all(page=page)
    return dict(**news)


@bp.route("/news")
@response(template_file="partials/news/cards.html")
def news():
    """news page"""
    page = request.args.get("page", type=int, default=1)
    news = NewsService().get_all(page=page)
    return dict(**news)


@bp.route("/projects")
@response(template_file="projects.html")
def projects():
    """projects page"""
    page = request.args.get("page", type=int, default=1)
    projects = ProjectService().get_all(page=page)
    # locale must be included in the dict in order to be normalized
    # DONT' use request.args.get('lang') as it will return None
    if request.headers.get("hx-projects"):
        return make_response(
            render_template("partials/projects/cards.html", **projects)
        )

    return dict(**projects)


@bp.route("/team")
@response(template_file="team.html")
def team():
    """team page"""
    team_members = TeamService().get_all(sort="order")
    return dict(**team_members)


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
        return add_toast(make_response(), "error", _("Invalid credentials"))

    if username != "a" or password != "a":
        return add_toast(make_response(), "error", _("Invalid credentials"))

    # Successful login - Use HX-Redirect header for redirection
    response = make_response()
    response.headers["HX-Redirect"] = url_for("app_views.dashboard")
    return add_toast(response, "success", _("Login successful"))


@bp.route("/dashboard")
@response(template_file="dashboard.html")
def dashboard():
    """Dashboard page"""
    tab_query = request.args.get("q")
    if tab_query is None:
        return dict(tab="projects")

    tab_content = dict(
        team=dict(temp="partials/dashboard/team.html", data=TeamService().get_all),
        projects=dict(
            temp="partials/dashboard/projects.html",
            data=ProjectService().get_all,
        ),
        knowledge_hub=dict(
            temp="partials/dashboard/knowledge-hub.html", data=CourseService().get_all
        ),
        subscribers=dict(
            temp="partials/dashboard/subscribers.html", data=SubscriberService().get_all
        ),
        news=dict(temp="partials/dashboard/news.html", data=NewsService().get_all),
    )
    template = tab_content.get(tab_query, {}).get("temp")
    data = tab_content.get(tab_query, {}).get("data", lambda: {})()

    return make_response(
        render_template(
            template,
            **data,
        )
    )


@bp.route("/knowledge-hub")
@response(template_file="knowledge-hub.html")
def knowledge_hub():
    """knowledge-hub page"""
    tab_query = request.args.get("q", "research")
    tab_content = dict(
        research=dict(
            temp="partials/knowledge-hub/research.html", data=ResearchService().get_all
        ),
        courses=dict(
            temp="partials/knowledge-hub/courses.html", data=CourseService().get_all
        ),
        podcasts=dict(
            temp="partials/knowledge-hub/podcasts.html", data=PodcastService().get_all
        ),
    )

    data = tab_content.get(tab_query, {}).get("data", lambda: {})()
    template = tab_content.get(tab_query, {}).get("temp")
    print("------DATA------>", data)
    if request.headers.get("hx-tab"):
        return make_response(render_template(template, **data))
    return dict(tab="research", **data)


@bp.route("/contact-us", methods=["POST"])
@rate_limit(limits=RateLimits.STRICT)
def contact_us():
    """contact-us page"""
    contact_us_serv = ManageContactUs()

    form_data = request.form.to_dict()

    if form_data:
        try:
            contact_us_serv.contact_us_message(form_data)
        except Exception as e:
            print("------Contact us ERROR------>", e)
            return add_toast(
                make_response("", 400), "error", _("Failed to send message")
            )

    return add_toast(
        make_response("", 200), "success", _("Your comment received successfully")
    )


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
    if category not in [
        "projects",
        "research",
        "courses",
        "podcasts",
        "news",
        "team",
        "users",
    ]:
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
