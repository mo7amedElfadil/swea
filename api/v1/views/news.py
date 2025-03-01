from flask import make_response, render_template, request
from flask_babel import gettext as _

from api.v1.views import bp
from app.services.news import NewsService
from utils.toast_notify import add_toast
from utils.view_modifiers import response


@bp.route("/dashboard/news/form", methods=["GET"])
@response(template_file="partials/dashboard/news-form.html")
def retrieve_form():
    """get news form"""
    return dict()

@bp.route("/dashboard/news/create", methods=["POST"])
@response(template_file="partials/dashboard/news-form.html")
def create_news():
    """Add a new news"""
    news_form = request.form.to_dict()
    img = request.files.get('image')
    news_form['image'] = img
    news_data = NewsService().create(news_form)
    return dict()

@bp.route("/dashboard/news/update", methods=["UPDATE"])
@response(template_file="partials/dashboard/news-form.html")
def update_news():
    """Add a new news"""
    if request.headers.get('hx-request') and request.method == "UPDATE":
      news_form = request.form.to_dict()
      img = request.files.get('image')
      news_form['image'] = img
      news_data = NewsService().create(news_form)
    return dict()
