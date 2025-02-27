from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.team_service import TeamService
from utils.toast_notify import add_toast

team_service = TeamService()


@bp.route("/dashboard/team-members", methods=["GET"])
def filter_team_members():
    """Filter team members by search string."""
    search_str = request.args.get("search", "")
    page = int(request.args.get("page", 1))

    # Fetch team members based on search string
    if search_str:
        team_members_res = team_service.search_team_members_by_name(search_str)
    else:
        team_members_res = team_service.get_all_team_members(page=page)

    total_pages = (len(team_members_res) // 5) + 1
    return make_response(
        render_template(
            "partials/dashboard/team_list.html",
            members=team_members_res,
            search=search_str,
            page=page,
            total_pages=total_pages,
        )
    )


@bp.route("/dashboard/new-team-member", methods=["GET", "POST"])
def add_team_member():
    """Add a new team member."""
    if request.method == "GET":
        return render_template("partials/dashboard/new_team_member_form.html")

    try:
        form_data = request.form.to_dict()
        files = request.files
        team_service.create_team_member(form_data, files)
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(
            resp, "error", _("An error occurred while creating the team member")
        )

    team_members = team_service.get_all_team_members()
    resp = make_response(
        render_template(
            "partials/dashboard/team.html",
            **team_members,
        )
    )
    return add_toast(resp, "success", _("Team member created successfully"))


@bp.route("/dashboard/update-team-member/<member_id>", methods=["GET", "POST"])
def update_team_member(member_id):
    """Update an existing team member."""
    if request.method == "GET":
        member_data = team_service.get_team_member_by_uuid(member_id)
        if not member_data:
            resp = make_response("", 404)
            return add_toast(resp, "error", _("Team member not found"))
        return render_template(
            "partials/dashboard/edit_team_member_form.html", team=member_data
        )

    try:
        form_data = request.form.to_dict()
        files = request.files
        team_service.update_team_member(member_id, form_data, files)
        members_res = team_service.get_all_team_members()
        resp = make_response(
            render_template(
                "partials/dashboard/team.html",
                **members_res,
            )
        )
        return add_toast(resp, "success", _("Team member updated successfully"))
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(resp, "error", _(str(e)))


@bp.route("/dashboard/delete-team-member/<member_id>", methods=["DELETE"])
def delete_team_member(member_id):
    """Delete a team member."""
    success = team_service.delete_team_member(member_id)
    if not success:
        resp = make_response("", 404)
        return add_toast(resp, "error", _("Team member not found"))

    members_res = team_service.get_all_team_members()
    resp = make_response(
        render_template(
            "partials/dashboard/team_list.html",
            members=members_res["members"],
        )
    )
    return add_toast(resp, "success", _("Team member deleted successfully"))
