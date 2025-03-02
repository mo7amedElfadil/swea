from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.news import NewsService
from utils.toast_notify import add_toast
from utils.view_modifiers import response


@bp.route("/dashboard/news/form", methods=["GET"])
@response(template_file="partials/dashboard/news-form.html")
def retrieve_form():
    """Get news form"""
    return dict()

@bp.route("/dashboard/news/create", methods=["POST"])
def create_news():
    """Create news"""
    news_form = request.form.to_dict()
    img = request.files.get('image')
    news_form['image'] = img
    try:
      news_data = NewsService().create(news_form)
    except Exception:
      pass
    return make_response()

@bp.route("/dashboard/news/update", methods=["PATCH"])
def update_news():
    """Update news"""
    news_form = request.form.to_dict()
    return make_response()


@bp.route("/dashboard/news/delete", methods=["DELETE"])
def delete_news():
    """Delelte news"""
    return make_response()
