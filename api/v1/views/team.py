from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services import TeamService
from utils.cache_mgr import cache_response, invalidate_cache
from utils.toast_notify import add_toast

team_service = TeamService()


@bp.route("/dashboard/team-members", methods=["GET"])
@cache_response()
def filter_team_members():
    """Filter team members by search string."""
    search_str = request.args.get("search", "")
    page = int(request.args.get("page", 1))

    # Fetch team members based on search string
    if search_str:
        team_members_res = team_service.search_team_members_by_name(search_str)
    else:
        team_members_res = team_service.get_all(
            page=page, sort='teams."order"'
        )

    return make_response(
        render_template(
            "partials/dashboard/team-list.html",
            **team_members_res,
            search=search_str,
        )
    )


@bp.route("/dashboard/new-team-member", methods=["GET", "POST"])
def add_team_member():
    """Add a new team member."""
    if request.method == "GET":
        return render_template(
            "partials/dashboard/team_member-form.html",
            form_action="/dashboard/new-team-member",
            team=None,
            submit_text=_("create_team_member"),
        )

    try:
        form_data = request.form.to_dict()
        files = request.files
        team_service.create_team_member(form_data, files)
    except Exception as e:
        print(e)
        resp = make_response(str(e), 400)
        return add_toast(
            resp,
            "error",
            _("An error occurred while creating the team member"),
        )

    team_members = team_service.get_all(sort='teams."order"')
    resp = make_response(
        render_template(
            "partials/dashboard/team.html",
            **team_members,
        )
    )
    invalidate_cache(["filter_team_members", "team"])
    return add_toast(resp, "success", _("Team member created successfully"))


@bp.route("/dashboard/update-team-member/<member_id>", methods=["GET", "POST"])
def update_team_member(member_id):
    """Update an existing team member."""
    if request.method == "GET":
        member_data = team_service.get_by_uuid(member_id)
        if not member_data:
            resp = make_response("", 404)
            return add_toast(resp, "error", _("Team member not found"))
        return render_template(
            "partials/dashboard/team_member-form.html",
            form_action=f"/dashboard/update-team-member/{member_id}",
            team=member_data,
            submit_text=_("update_team_member"),
        )

    try:
        form_data = request.form.to_dict()
        files = request.files
        team_service.update_team_member(member_id, form_data, files)
        members_res = team_service.get_all(sort='teams."order"')
        resp = make_response(
            render_template(
                "partials/dashboard/team.html",
                **members_res,
            )
        )
        invalidate_cache(["filter_team_members", "team"])
        return add_toast(
            resp, "success", _("Team member updated successfully")
        )
    except Exception as e:
        resp = make_response(str(e), 400)
        return add_toast(resp, "error", _(str(e)))


@bp.route("/dashboard/delete-team-member/<member_id>", methods=["DELETE"])
def delete_team_member(member_id):
    """Delete a team member."""
    order = team_service.get_by_uuid(member_id).get("order")
    success = team_service.delete(member_id)
    if not success:
        resp = make_response("", 404)
        return add_toast(resp, "error", _("Team member not found"))

    # Update the order of other team members
    team_service.update_team_member_order(order=order + 1, mode=-1)

    members_res = team_service.get_all(sort='teams."order"')
    resp = make_response(
        render_template(
            "partials/dashboard/team.html",
            **members_res,
        )
    )
    invalidate_cache(["filter_team_members", "team"])
    return add_toast(resp, "success", _("Team member deleted successfully"))
