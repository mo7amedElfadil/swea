from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.course_service import CourseService
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
