from flask import make_response, request
from api.v1.views import bp
from utils.view_modifiers import response

@bp.route("/", methods=["GET", "POST"])
@response(template_file="index.html")
def index():
    if request.headers.get("hx-request"):
        html = '<h2> this markup from backend, open network tab</h2>'
        return make_response(html)
    return {"user" : "John Doe"}
