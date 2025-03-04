from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.project_service import ProjectService
from utils.toast_notify import add_toast, with_toast

project_service = ProjectService()


@bp.route("/dashboard/projects", methods=["GET"])
def filter_projects():
    """Filter projects by status and search string"""
    search_str = request.args.get("search", "")
    status = request.args.get("filter", "all")
    page = int(request.args.get("page", 1))

    projects = project_service.get_all(status=status, page=page)
    data = projects.get('projects')
    del projects['projects']

    return make_response(
        render_template(
            "partials/dashboard/project-list.html",
            data=data,
            search=search_str,
            filter=status,
            **projects
        )
    )

@bp.route("/dashboard/new-project", methods=["GET", "POST"])
@with_toast
def add_project():
    """Add a new project"""
    if request.method == "GET":
        return render_template("partials/dashboard/new_project_form.html")

    try:
        form_data = request.form.to_dict()
        files = request.files
        new_project = project_service.create_project(form_data, files)
        return dict(
                toast={"type": "success", "message": "Project created successfully"},
        )
    except Exception as e:
        return dict(
                toast={"type": "error", "message": _("Unexpected error occurred")}
        )


@bp.route("/dashboard/update-project/<project_id>", methods=["GET", "POST"])
def update_project(project_id):
    """Update an existing project"""
    if request.method == "GET":
        project_data = project_service.get_project_by_uuid(project_id)

        if not project_data:
            resp = make_response("", 404)
            return add_toast(resp, "error", _("Project not found"))

        return render_template(
            "partials/dashboard/edit_project_form.html", project=project_data
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
                projects=project_service.get_all_projects(),
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
            "partials/dashboard/project_list.html",
            projects=project_service.get_all_projects(),
        )
    )

    return add_toast(resp, "success", _("Project deleted successfully"))
