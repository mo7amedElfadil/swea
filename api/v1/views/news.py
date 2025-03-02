from flask import make_response, redirect, render_template, request, url_for
from flask_babel import gettext as _
from marshmallow import ValidationError

from api.v1.views import bp
from app.services.news import NewsService
from utils.toast_notify import add_toast
from utils.view_modifiers import response


@bp.route("/dashboard/news/form", methods=["GET"])
@response(template_file="partials/dashboard/news-form.html")
def retrieve_form():
    """Get news form"""
    return dict()

@bp.route("/dashboard/news", methods=["GET"])
@response(template_file="partials/dashboard/news-list.html")
def get_news():
    """Get news paginated"""
    page = request.args.get("page", type=int, default=1)
    news = NewsService().get_all(page=page)
    data = news.get('news')
    del news['news']
    return dict(data=data, **news)


@bp.route("/dashboard/news", methods=["POST"])
def create_news():
    """Create news"""
    news_form = request.form.to_dict()
    img = request.files.get('image')
    news_form['image'] = img

    try:
      news = NewsService().create(news_form)
      return add_toast(
        make_response("News created successfully", 201),
        "success",
        _("News created successfully")
      )
    except ValidationError as e:
        return add_toast(make_response(str(e), 400),
                         "error",
                         _("An error occurred while"+
                           "creating the news"
                           ))
    except Exception as e:
        return add_toast(make_response(
        str(e), 500),
        "error",
        _("Unexpected error occurred"))


@bp.route("/dashboard/news/<news_id>", methods=["PUT", "PATCH"])
def update_news(news_id):
    """Update news"""
    news_form = request.form.to_dict()
    return make_response()


@bp.route("/dashboard/news/<news_id>", methods=["DELETE"])
def delete_news(news_id):
    """Delelte news"""
    try:
      NewsService().delete(news_id)
      # 303 See Other:
      # This status code tells the client to fetch the resource,
      # from the Location header using a GET request.
      resp = redirect(url_for("app_views.get_news"), code=303)

      return resp
    except Exception as e:
      return add_toast(make_response(str(e), 500),
                "error",
                _("Unexpected error occurred"))
