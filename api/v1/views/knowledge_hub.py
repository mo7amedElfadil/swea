from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.course_service import CourseService
from app.services.podcast_service import PodcastService
from app.services.research_service import ResearchService
from utils.toast_notify import add_toast

course_service = CourseService()


@bp.route("/dashboard/knowledge-hub", methods=["GET"])
def knowledge_hub_tabs():
    """knowledge-hub tabs."""
    tab_query = request.args.get("tab", "courses")
    tab_mapper = {
        "courses": "partials/dashboard/knowledge_hub/courses.html",
        "podcasts": "partials/dashboard/knowledge_hub/podcasts.html",
        "researches": "partials/dashboard/knowledge_hub/researches.html",
    }

    if request.headers.get("hx-tab"):
        return make_response(
            render_template(
                tab_mapper.get(
                    tab_query, "partials/dashboard/knowledge_hub/courses.html"
                ),
            )
        )
    return dict()


@bp.route("/dashboard/knowledge-hub/courses", methods=["GET"])
def get_courses():
    """Get courses."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    courses = course_service.get_all(page=page, search=search)
    return render_template(
        "partials/dashboard/knowledge_hub/courses.html", courses=courses
    )
