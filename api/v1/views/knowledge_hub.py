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
    tab_content = dict(
            courses=dict(
                temp="partials/dashboard/knowledge_hub/courses.html",
                data=dict
                ),
            podcasts=dict(
                temp="partials/dashboard/knowledge_hub/podcasts.html",
                data=dict
                ),
            researches=dict(
                temp="partials/dashboard/knowledge_hub/researches.html",
                data=dict
                ),
            )

    if request.headers.get("hx-tab"):
        template = tab_content.get(tab_query, {}).get("temp")
        data = tab_content.get(tab_query,{}).get("data", lambda : {})()
        return make_response(
            render_template(template, **data)
        )
    return dict()


@bp.route("/dashboard/knowledge-hub/form", methods=["GET"])
def knowledge_hub_form():
    """knowledge-hub form."""
    query = request.args.get("q", "courses")
    form_content = dict(
        courses="partials/dashboard/knowledge_hub/course-form.html",
        podcasts="partials/dashboard/knowledge_hub/podcast-form.html",
        researches="partials/dashboard/knowledge_hub/research-form.html",
    )

    return make_response(render_template(
        form_content.get(
            query,
            "partials/dashboard/knowledge_hub/course-form.html"
            )
        )
    )


@bp.route("/dashboard/knowledge-hub/courses", methods=["GET"])
def get_courses():
    """Get courses."""
    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    courses = course_service.get_all(page=page, search=search)
    return render_template(
        "partials/dashboard/knowledge_hub/courses.html", courses=courses
    )
