from flask import flash, make_response, redirect, render_template, request, url_for
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.project_service import ProjectService

# Initialize the service with static dummy data
project_service = ProjectService()


@bp.route("/dashboard/new-project", methods=["GET"])
def new_project():
    """Render the form to add a new project"""
    return render_template("partials/dashboard/new_project_form.html")


@bp.route("/dashboard/add-project", methods=["POST"])
def add_project():
    """Add a new project"""
    name = request.form.get("name")
    description = request.form.get("description")
    status = request.form.get("status", "active")

    if not name or not description:
        flash(_("project_name_and_description_required"), "error")
        return redirect(url_for("dashboard"))

    project_service.add_project(name=name, description=description, status=status)
    flash(_("project_added_successfully"), "success")
    return make_response(render_template("partials/dashboard/projects.html"))


@bp.route("/dashboard/edit-project/<int:project_id>", methods=["GET"])
def edit_project(project_id):
    """Render the form to edit an existing project"""
    project = project_service.get_project_by_id(project_id)
    if not project:
        flash(_("project_not_found"), "error")
        return redirect(url_for("dashboard"))

    return render_template("partials/dashboard/edit_project_form.html", project=project)


@bp.route("/dashboard/update-project/<int:project_id>", methods=["POST"])
def update_project(project_id):
    """Update an existing project"""
    name = request.form.get("name")
    description = request.form.get("description")
    status = request.form.get("status", "active")

    if not name or not description:
        flash(_("project_name_and_description_required"), "error")
        return redirect(url_for("dashboard"))

    project_service.update_project(
        project_id=project_id, name=name, description=description, status=status
    )
    flash(_("project_updated_successfully"), "success")
    return make_response(render_template("partials/dashboard/projects.html"))


@bp.route("/dashboard/delete-project/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a project"""
    success = project_service.delete_project(project_id)
    if not success:
        flash(_("project_not_found"), "error")
        return make_response("", 404)

    flash(_("project_deleted_successfully"), "success")
    return make_response("", 200)
