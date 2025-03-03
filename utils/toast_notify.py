import json
import werkzeug
import werkzeug.wrappers
from functools import wraps
from typing import Any, Callable, Dict, Literal, TypeVar, cast

from flask import Response, make_response, request

# Type variables for the decorator pattern
F = TypeVar("F", bound=Callable[..., Any])
ToastType = Literal["success", "error", "warning", "info"]


def with_toast(f):
    """
    Decorator to add toast notification to HTMX responses

    Args:
        toast_type: Type of toast ('success', 'error', 'warning', 'info')
        message: Message to display in the toast

    Example usage:
    ```
    @bp.route('/create-item', methods=['POST'])
    @with_toast('success', 'Item created successfully')
    def create_item():
        # Your logic here
        return render_template('partials/item.html', item=new_item)
    ```
    """

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any):
        response = f(*args, **kwargs)
        toast = dict(type="success", message="Success")
        if isinstance(response, (werkzeug.wrappers.Response, Response)):
            toast = response.headers.get('hx-toast')
            if toast:
                toast = json.loads(toast)
                response.headers["HX-Trigger"] = json.dumps({"showToast": toast})
            return response
        # Only add toast for HTMX requests
        if isinstance(response, dict) and request.headers.get("hx-request"):
            toast = response.get("toast")
            if toast is None:
                return response
            # Create or update the HX-Trigger header
            response = make_response(response)
            trigger_header = response.headers.get("HX-Trigger", "{}")
            try:
                triggers: Dict[str, Any] = json.loads(trigger_header)
            except ValueError:
                triggers = {}

            # Add the showToast event
            triggers["showToast"] = dict(
                type=toast.get("type"),
                message=toast.get("message")
                )

            # Update the header
            response.headers["HX-Trigger"] = json.dumps(triggers)

        return response

    return decorated_function


def add_toast(response: Response, toast_type: ToastType, message: str) -> Response:
    """
    Add toast notification to an existing response object

    Args:
        response: Flask response object to modify
        toast_type: Type of toast ('success', 'error', 'warning', 'info')
        message: Message to display in the toast

    Returns:
        Modified Flask response with toast trigger added

    Example usage:
    ```
    @bp.route('/delete-item/<int:id>', methods=['DELETE'])
    def delete_item(id):
        # Delete logic here
        response = make_response("", 200)
        return add_toast(response, 'success', f'Item {id} deleted successfully')
    ```
    """
    if request.headers.get("HX-Request") == "true":
        trigger_header = response.headers.get("HX-Trigger", "{}")
        try:
            triggers: Dict[str, Any] = json.loads(trigger_header)
        except ValueError:
            triggers = {}

        triggers["showToast"] = {"type": toast_type, "message": message}

        response.headers["HX-Trigger"] = json.dumps(triggers)

    return response
