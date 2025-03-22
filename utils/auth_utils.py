from functools import wraps

from flask import make_response, redirect, request, session, url_for
from flask_babel import gettext as _

from utils.toast_notify import add_toast


def login_required(redirect_to="app_views.login", message=None):
    """
    Decorator to protect routes that require authentication.

    Args:
        redirect_to (str): The endpoint to redirect unauthenticated users to
        message (str, optional): Custom message for unauthenticated access attempts
            If None, a default message will be used

    Returns:
        Function: The decorated view function

    Usage:
        ```
        @bp.route('/protected')
        @login_required()
        def protected_route():
            return 'This is protected'

        @bp.route('/admin-only')
        @login_required(message='Admin access required')
        def admin_route():
            return 'Admin area'
        ```
    """

    def decorator(view_function):
        @wraps(view_function)
        def wrapped_view(*args, **kwargs):
            if "user" not in session:
                if request.headers.get("HX-Request") == "true":
                    response = make_response()
                    response.headers["HX-Redirect"] = url_for(redirect_to)
                    error_message = message or _("Please log in to access this page")
                    return add_toast(response, "error", error_message)
                else:
                    return redirect(url_for(redirect_to))

            return view_function(*args, **kwargs)

        return wrapped_view

    return decorator
