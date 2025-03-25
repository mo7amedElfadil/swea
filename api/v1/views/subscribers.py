from flask import make_response, render_template, request
from flask_babel import gettext as _
from psycopg2.errors import UniqueViolation

from api.v1.views import bp
from app.services import SubscriberService
from utils.auth_utils import login_required
from utils.toast_notify import add_toast

subscriber_service = SubscriberService()


@bp.route("/subscribe", methods=["POST"])
def subscribe():
    """Subscribe to the newsletter."""
    form_data = request.form.to_dict()

    if form_data:
        try:
            subscriber_service.create_subscriber(form_data)
        except UniqueViolation:
            return add_toast(
                make_response("", 409), "error", _("Email already subscribed")
            )
        except ValueError as ve:
            return add_toast(make_response("", 400), "error", str(ve))
        except Exception as e:
            return add_toast(make_response("", 400), "error", _("Failed to subscribe"))

    return add_toast(make_response("", 200), "success", _("Thank you for subscribing"))


@bp.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    """Unsubscribe from the newsletter."""
    subscriber_email = request.args.get("email")

    if subscriber_email:
        try:
            subscriber_service.delete_subscriber(subscriber_email)
        except Exception as e:
            return add_toast(
                make_response("", 400), "error", _("Failed to unsubscribe")
            )

    return add_toast(make_response("", 200), "success", _("Unsubscribed successfully"))


@bp.route("/dashboard/subscribers", methods=["GET"])
def filter_subscribers():
    """Filter subscribers by search string."""
    search_str = request.args.get("search", "")
    page = int(request.args.get("page", 1))

    # Fetch subscribers based on search string
    if search_str:
        subscribers_res = subscriber_service.search_subscribers_by_email(search_str)
    else:
        subscribers_res = subscriber_service.get_all(page=page)

    return make_response(
        render_template(
            "partials/dashboard/subscribers-list.html",
            **subscribers_res,
            search=search_str,
        )
    )


@bp.route("/dashboard/broadcast-email", methods=["GET", "POST"])
def send_broadcast_email():
    """Send a broadcast email to all subscribers."""

    if request.method == "GET":
        return render_template("partials/dashboard/subscribers_broadcast-form.html")

    form_data = request.form.to_dict()

    if form_data:
        try:
            subscriber_service.send_broadcast_email(form_data)
        except Exception as e:
            print(e)
            return add_toast(
                make_response("", 400), "error", _("Failed to send broadcast email")
            )

    subscribers = subscriber_service.get_all()

    resp = make_response(
        render_template(
            "partials/dashboard/subscribers.html",
            **subscribers,
        ),
        200,
    )

    return add_toast(resp, "success", _("Broadcast email sent successfully"))


@bp.route("/dashboard/export-subscribers", methods=["GET"])
@login_required()
def export_subscribers():
    """Export subscribers to an Excel file."""
    excel_file, file_name = subscriber_service.export_subscribers()

    response = make_response(excel_file.read())
    response.headers["Content-Disposition"] = f"attachment;filename={file_name}"
    response.headers["Content-Type"] = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    return add_toast(response, "success", _("Subscribers exported successfully"))
