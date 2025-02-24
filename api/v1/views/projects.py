from flask import make_response, redirect, render_template, request
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
    try:
        form_data = request.form.to_dict()
        print("=====>", form_data)
        files = request.files
        project_service.create_project(form_data, files)
    except Exception as e:
        print(e)
        return redirect("/dashboard?q=projects")

    return make_response(
        render_template(
            "partials/dashboard/projects.html",
            projects=project_service.get_all_projects(),
        )
    )


@bp.route("/dashboard/edit-project/<project_id>", methods=["GET"])
def edit_project(project_id):
    """Render the form to edit an existing project"""
    project = project_service.get_project_by_uuid(project_id)
    if not project:
        return redirect("/dashboard?q=projects")

    print("==TO-UPDATE===>", project)

    return render_template("partials/dashboard/edit_project_form.html", project=project)


@bp.route("/dashboard/update-project/<project_id>", methods=["POST"])
def update_project(project_id):
    """Update an existing project"""
    try:
        form_data = request.form.to_dict()

        files = request.files
        project_service.update_project(project_id, form_data, files)
        return make_response(
            render_template(
                "partials/dashboard/projects.html",
                projects=project_service.get_all_projects(),
            )
        )
    except Exception as e:
        return redirect("/dashboard?q=projects")


@bp.route("/dashboard/delete-project/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a project"""
    success = project_service.delete_project(project_id)
    if not success:
        return make_response("", 404)

    return make_response(
        render_template(
            "partials/dashboard/projects.html",
            projects=project_service.get_all_projects(),
        )
    )
