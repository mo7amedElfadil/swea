from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.project_service import ProjectService
from utils.toast_notify import add_toast
from utils.view_modifiers import response

project_service = ProjectService()


@bp.route("/projects/<uuid>", methods=["GET"])
@response(template_file="project-page.html")
def project_page(uuid):
    """Project page"""
    project = project_service.get_project_by_uuid(uuid)
    if not project:
        return add_toast(make_response("", 404), "error", _("Project not found"))

    return dict(project=project)


@bp.route("/dashboard/projects", methods=["GET"])
def filter_projects():
    """Filter projects by status and search string"""
    search_str = request.args.get("search", "")
    status = request.args.get("filter", "all")
    page = int(request.args.get("page", 1))

    if search_str:
        projects = project_service.search_projects_by_title(search_str)
    else:
        if status in ["ongoing", "completed"]:
            projects = project_service.get_all(page=page, status=status)
        else:
            projects = project_service.get_all(page=page)

    return make_response(
        render_template(
            "partials/dashboard/project-list.html",
            **projects,
            search=search_str,
            filter=status,
        )
    )


@bp.route("/dashboard/new-project", methods=["GET", "POST"])
@response(template_file="partials/dashboard/project-form.html")
def add_project():
    """Add a new project"""
    if request.method == "POST":
        try:
            form_data = request.form.to_dict()
            files = request.files
            project_service.create_project(form_data, files)
            resp = make_response(
                render_template(
                    "partials/dashboard/projects.html", **project_service.get_all()
                )
            )
            return add_toast(resp, "success", _("Project created successfully"))
        except Exception as e:
            print(f"Error: {e}")
            resp = make_response(
                render_template(
                    "partials/dashboard/projects.html",
                    **project_service.get_all(),
                )
            )
            return add_toast(resp, "error", "Unexpected error occurred")

    return dict()


@bp.route("/dashboard/update-project/<project_id>", methods=["GET", "POST"])
def update_project(project_id):
    """Update an existing project"""
    if request.method == "GET":
        project_data = project_service.get_project_by_uuid(project_id)

        if not project_data:
            resp = make_response("", 404)
            return add_toast(resp, "error", _("Project not found"))

        return render_template(
            "partials/dashboard/project-form.html", project=project_data
        )

    try:
        form_data = request.form.to_dict()
        files = request.files
        print(f"Received form data: {form_data}")
        print(f"Received files: {files.keys()}")
        project_service.update_project(project_id, form_data, files)
        resp = make_response(
            render_template(
                "partials/dashboard/projects.html",
                **project_service.get_all(),
            )
        )
        return add_toast(resp, "success", _("Project updated successfully"))
    except Exception as e:
        resp = make_response(e, 400)
        return add_toast(resp, "error", _(e))


@bp.route("/dashboard/delete-project/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a project"""
    success = project_service.delete_project(project_id)
    if not success:
        resp = make_response("", 404)
        return add_toast(resp, "error", _("Project not found"))

    resp = make_response(
        render_template(
            "partials/dashboard/project-list.html",
            **project_service.get_all(),
        )
    )

    return add_toast(resp, "success", _("Project deleted successfully"))
