from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.news import NewsService
from utils.toast_notify import add_toast
from utils.view_modifiers import response


@bp.route("/dashboard/news/create", methods=["GET", "POST"])
@response(template_file="partials/dashboard/news-form.html")
def create_news():
    """Add a new news"""
    if request.headers.get('hx-request'):
      pass
    return dict()
