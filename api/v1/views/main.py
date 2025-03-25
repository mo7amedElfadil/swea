from typing import Any, Dict, Optional, Protocol, Type

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
from app.services import (
    CourseService,
    ManageContactUs,
    NewsService,
    PodcastService,
    ProjectService,
    ResearchService,
    SubscriberService,
    TeamService,
)
from config import Config
from utils.auth_utils import login_required
from utils.cache_mgr import cache_response
from utils.image_processing import ImageProcessing
from utils.rate_limiter import RateLimits, rate_limit
from utils.referrer_modifier import modify_referrer_lang
from utils.toast_notify import add_toast
from utils.view_modifiers import response

img = ImageProcessing()

# Mapping for dynamic tab-based views
TAB_CONTENT_MAP = {
    "dashboard": {
        "team": ("partials/dashboard/team.html", TeamService),
        "projects": ("partials/dashboard/projects.html", ProjectService),
        "knowledge_hub": ("partials/dashboard/knowledge-hub.html", CourseService),
        "subscribers": ("partials/dashboard/subscribers.html", SubscriberService),
        "news": ("partials/dashboard/news.html", NewsService),
    },
    "knowledge_hub": {
        "research": ("partials/knowledge-hub/research.html", ResearchService),
        "courses": ("partials/knowledge-hub/courses.html", CourseService),
        "podcasts": ("partials/knowledge-hub/podcasts.html", PodcastService),
    },
}


class PaginatedService(Protocol):
    def get_all(self, page: int = 1, **kwargs: Any) -> Dict[str, Any]:
        """Method signature required for paginated services."""
        ...


def get_paginated_data(
    service: Type[PaginatedService], page: int = 1, sort: Optional[str] = None
) -> Dict[str, Any]:
    """Helper function to fetch paginated and sorted data from a service."""
    return (
        service().get_all(page=page, sort=sort)
        if sort
        else service().get_all(page=page)
    )


@bp.route("/")
@response(template_file="index.html")
@cache_response()
def index():
    """Home page"""
    return get_paginated_data(NewsService)


@bp.route("/news")
@response(template_file="partials/news/cards.html")
@cache_response()
def news():
    """News page"""
    return get_paginated_data(NewsService)


@bp.route("/projects")
@response(template_file="projects.html")
@cache_response()
def projects():
    """Projects page"""
    page = request.args.get("page", type=int, default=1)
    projects = get_paginated_data(
        ProjectService, page, sort="COALESCE(date_of_completion, created_at) DESC"
    )

    if request.headers.get("hx-projects"):
        return make_response(
            render_template("partials/projects/cards.html", **projects)
        )

    return projects


@bp.route("/team")
@response(template_file="team.html")
@cache_response()
def team():
    """Team page"""
    return get_paginated_data(TeamService, sort='teams."order"')


@bp.route("/login", methods=["GET", "POST"])
@response(template_file="auth.html")
def login():
    """Login page with HTMX"""
    if request.method == "GET":
        return {}

    username, password = request.form.get("username"), request.form.get("password")

    if not username or not password or (username != "sawsan" or password != "sawsan"):
        return add_toast(make_response(), "error", _("Invalid credentials"))

    session["user"] = username
    response = make_response()
    response.headers["HX-Redirect"] = url_for("app_views.dashboard")
    return add_toast(response, "success", _("Login successful"))


@bp.route("/dashboard")
@login_required()
@response(template_file="dashboard.html")
def dashboard():
    """Dashboard page"""
    tab_query = request.args.get("q")
    if tab_query is None:
        return dict(tab="projects")

    tab_info = TAB_CONTENT_MAP["dashboard"].get(tab_query)

    if not tab_info:
        return dict(tab="projects")

    template, service = tab_info
    data = get_paginated_data(service, sort="created_at DESC")

    return make_response(render_template(template, **data))


@bp.route("/knowledge-hub")
@response(template_file="knowledge-hub.html")
@cache_response()
def knowledge_hub():
    """Knowledge Hub page"""
    tab_query = request.args.get("q", "research")
    page = request.args.get("page", type=int, default=1)

    tab_info = TAB_CONTENT_MAP["knowledge_hub"].get(tab_query)
    if not tab_info:
        return dict(tab="research")

    template, service = tab_info
    data = get_paginated_data(service, page, sort="created_at DESC")

    if tab_query == "courses":
        data = CourseService().process_courses_data(data)

    if request.headers.get("hx-tab"):
        return make_response(render_template(template, **data))

    return dict(tab="research", **data)


@bp.route("/knowledge-hub/filter-courses")
@cache_response()
def filter_courses():
    """Filter courses based on selected course name or tag."""
    course_name, tag, locale = (
        request.args.get("course_name"),
        request.args.get("tag"),
        request.args.get("locale", "en"),
    )

    courses_data = get_paginated_data(CourseService, sort="created_at DESC")
    courses_data["data"] = [
        course
        for course in courses_data.get("data", [])
        if (not course_name or course["course_name"][locale] == course_name)
        and (not tag or tag in course["tags"][locale])
    ]

    return render_template("partials/cards/course.html", **courses_data)


@bp.route("/contact-us", methods=["POST"])
@rate_limit(limits=RateLimits.STRICT)
def contact_us():
    """Handle contact-us messages"""
    form_data = request.form.to_dict()

    if form_data:
        try:
            ManageContactUs().contact_us_message(form_data)
        except Exception:
            return add_toast(
                make_response("", 400), "error", _("Failed to send message")
            )

    return add_toast(
        make_response("", 200), "success", _("Your comment received successfully")
    )


@bp.route("/set_language")
def set_language():
    """Set user language preference"""
    lang = request.args.get("lang")
    if lang in Config.BABEL_SUPPORTED_LOCALES:
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
    """Upload an image to the appropriate category"""
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

    file = request.files.get("file")
    if not file:
        return {"error": "No file uploaded"}, 400

    saved_path = img.save_image(file, category, uuid)
    return (
        {"message": "Image uploaded successfully", "path": saved_path}
        if saved_path
        else {"error": "Invalid file type"}
    ), 400


@bp.route("/uploads/<path:filename>")
def get_image(filename):
    """Retrieve uploaded images"""
    return send_from_directory(Config.UPLOAD_FOLDER, filename)
