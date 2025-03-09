from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.course_service import CourseService
from app.services.member_service import MemberService
from app.services.podcast_service import PodcastService
from app.services.research_service import ResearchService
from utils.toast_notify import add_toast


@bp.route("/dashboard/knowledge-hub", methods=["GET"])
def get_knowledge_hub_data():
    """
    Unified route to handle fetching data for courses, podcasts, and researches.
    """
    tab = request.args.get("tab", "courses")

    # Map tabs to their respective services and templates
    service_mapper = {
        "courses": CourseService(),
        "podcasts": PodcastService(),
        "researches": ResearchService(),
    }
    template_mapper = {
        "courses": "partials/dashboard/knowledge_hub/courses.html",
        "podcasts": "partials/dashboard/knowledge_hub/podcasts.html",
        "researches": "partials/dashboard/knowledge_hub/researches.html",
    }

    # Validate the requested tab
    if tab not in service_mapper or tab not in template_mapper:
        return {"error": _("Invalid tab")}, 400

    # Fetch pagination and search parameters
    page = request.args.get("page", 1, type=int)

    # Fetch data using the appropriate service
    service = service_mapper[tab]

    data = service.get_all(page=page, deleted_at=None)
    # Render the appropriate template
    return make_response(render_template(template_mapper[tab], **data, active_tab=tab))


@bp.route("/dashboard/knowledge-hub/form", methods=["GET"])
def knowledge_hub_form():
    """knowledge-hub form."""
    method = request.args.get("m", "CREATE")
    query = request.args.get("q", "courses")
    uuid = request.args.get("uuid", None)
    form_content = dict(
        courses=dict(
            temp="partials/dashboard/knowledge_hub/courses-form.html",
            data=CourseService().get_by_uuid,
        ),
        podcasts=dict(
            temp="partials/dashboard/knowledge_hub/podcasts-form.html",
            data=PodcastService().get_by_uuid,
        ),
        researches=dict(
            temp="partials/dashboard/knowledge_hub/researches-form.html",
            data=ResearchService().get_by_uuid,
        ),
    )

    template = form_content.get(query, {}).get("temp")
    if method == "UPDATE":
        data = form_content.get(query).get("data", lambda: {})(uuid)
    else:
        data = {}

    return make_response(render_template(
        template,
        update=method == "UPDATE",
        **data,
        )
    )


@bp.route("/dashboard/knowledge-hub/courses", methods=["GET"])
def get_courses():
    """Get courses."""
    course_service = CourseService()
    search = request.args.get("search", "")
    courses = course_service.search_courses_by_title(search)
    return render_template(
        "partials/dashboard/knowledge_hub/courses-list.html", **courses
    )


@bp.route("/dashboard/knowledge-hub/courses", methods=["POST"])
def create_course():
    """Create a new course."""
    course_service = CourseService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        course_service.create_course(form_data, files)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while creating the course")
        )

    courses = course_service.get_all()
    resp = make_response(
        render_template("partials/dashboard/knowledge_hub/courses.html", **courses)
    )
    return add_toast(resp, "success", _("Course created successfully"))


@bp.route("/dashboard/knowledge-hub/courses/<course_id>", methods=["PATCH", "PUT"])
def update_course(course_id):
    """Update an existing course."""
    course_service = CourseService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        course_service.update_course(course_id, form_data, files)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while updating the course")
        )

    courses = course_service.get_all()
    resp = make_response(
        render_template("partials/dashboard/knowledge_hub/courses.html", **courses)
    )
    return add_toast(resp, "success", _("Course updated successfully"))


@bp.route("/dashboard/knowledge-hub/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course."""
    course_service = CourseService()
    try:
        course_service.delete(course_id)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while deleting the course")
        )

    courses = course_service.get_all()
    resp = make_response(
        render_template("partials/dashboard/knowledge_hub/courses-list.html", **courses)
    )
    return add_toast(resp, "success", _("Course deleted successfully"))


@bp.route("/dashboard/knowledge-hub/podcasts", methods=["GET"])
def get_podcasts():
    """Get podcasts."""
    podcast_service = PodcastService()
    search = request.args.get("search", "")
    podcasts = podcast_service.search_podcasts_by_title(search)
    return render_template(
        "partials/dashboard/knowledge_hub/podcasts-list.html", **podcasts
    )


@bp.route("/dashboard/knowledge-hub/podcasts", methods=["POST"])
def create_podcast():
    """Create a new podcast."""
    podcast_service = PodcastService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        podcast_service.create_podcast(form_data, files)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while creating the podcast")
        )

    podcasts = podcast_service.get_all()
    resp = make_response(
        render_template("partials/dashboard/knowledge_hub/podcasts.html", **podcasts)
    )
    return add_toast(resp, "success", _("Podcast created successfully"))


@bp.route("/dashboard/knowledge-hub/podcasts/<podcast_id>", methods=["PUT", "PATCH"])
def update_podcast(podcast_id):
    """Update an existing podcast."""
    podcast_service = PodcastService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        podcast_service.update_podcast(podcast_id, form_data, files)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while updating the podcast")
        )

    podcasts = podcast_service.get_all()
    resp = make_response(
        render_template("partials/dashboard/knowledge_hub/podcasts.html", **podcasts)
    )
    return add_toast(resp, "success", _("Podcast updated successfully"))


@bp.route("/dashboard/knowledge-hub/podcasts/<podcast_id>", methods=["DELETE"])
def delete_podcast(podcast_id):
    """Delete a podcast."""
    podcast_service = PodcastService()
    try:
        podcast_service.delete(podcast_id)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while deleting the podcast")
        )

    podcasts = podcast_service.get_all()
    resp = make_response(
        render_template(
            "partials/dashboard/knowledge_hub/podcasts-list.html", **podcasts
        )
    )
    return add_toast(resp, "success", _("Podcast deleted successfully"))


@bp.route("/dashboard/knowledge-hub/researches", methods=["GET"])
def get_researches():
    """Get researches."""
    research_service = ResearchService()
    search = request.args.get("search", "")
    researches = research_service.search_researches_by_title(search)
    return render_template(
        "partials/dashboard/knowledge_hub/researches-list.html", **researches
    )


@bp.route("/dashboard/knowledge-hub/researches", methods=["POST"])
def create_research():
    """Create a new research."""
    research_service = ResearchService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        research_service.create_research(form_data, files)
    except Exception as e:
        print("============ERROR============", e)
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while creating the research")
        )

    researches = research_service.get_all()
    resp = make_response(
        render_template(
            "partials/dashboard/knowledge_hub/researches.html", **researches
        )
    )
    return add_toast(resp, "success", _("Research created successfully"))


@bp.route("/dashboard/knowledge-hub/researches/<research_id>", methods=["PATCH", "PUT"])
def update_research(research_id):
    """Update an existing research."""
    research_service = ResearchService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        research_service.update_research(research_id, form_data, files)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while updating the research")
        )

    researches = research_service.get_all()
    resp = make_response(
        render_template(
            "partials/dashboard/knowledge_hub/researches.html", **researches
        )
    )
    return add_toast(resp, "success", _("Research updated successfully"))


@bp.route("/dashboard/knowledge-hub/researches/<research_id>", methods=["DELETE"])
def delete_research(research_id):
    """Delete a research."""
    research_service = ResearchService()
    try:
        research_service.delete(research_id)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while deleting the research")
        )

    researches = research_service.get_all()
    resp = make_response(
        render_template(
            "partials/dashboard/knowledge_hub/researches-list.html", **researches
        )
    )
    return add_toast(resp, "success", _("Research deleted successfully"))


@bp.route("/dashboard/knowledge-hub/members", methods=["GET"])
def get_members():
    """Get members."""
    member_service = MemberService()
    search = request.args.get("search", "")
    members = member_service.search_members_by_name(search)
    return render_template("partials/dashboard/knowledge_hub/members-list.html", **members)


@bp.route("/dashboard/knowledge-hub/members", methods=["POST"])
def create_member():
    """Create a new member."""
    member_service = MemberService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        member_service.create_member(form_data, files)
    except Exception as e:
        print("============ERROR============", e)
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while creating the member")
        )


    return add_toast(make_response(), "success", _("Member created successfully"))


@bp.route("/dashboard/knowledge-hub/members/<member_id>", methods=["PUT", "PATCH"])
def update_member(member_id):
    """Update an existing member."""
    member_service = MemberService()

    try:
        form_data = request.form.to_dict()
        files = request.files
        member_service.update_member(member_id, form_data, files)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while updating the member")
        )

    members = member_service.get_all()
    resp = make_response(
        render_template("partials/dashboard/knowledge_hub/members.html", **members)
    )
    return add_toast(resp, "success", _("Member updated successfully"))


@bp.route("/dashboard/knowledge-hub/members/<member_id>", methods=["DELETE"])
def delete_member(member_id):
    """Delete a member."""
    member_service = MemberService()
    try:
        member_service.delete(member_id)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while deleting the member")
        )

    members = member_service.get_all()
    resp = make_response(
        render_template("partials/dashboard/knowledge_hub/members.html", **members)
    )
    return add_toast(resp, "success", _("Member deleted successfully"))
