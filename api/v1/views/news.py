from flask import make_response, render_template, request
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
    news_list = NewsService().get_all(page=page)
    return dict(news=news_list)

@bp.route("/dashboard/news", methods=["POST"])
def create_news():
    """Create news"""
    news_form = request.form.to_dict()
    img = request.files.get('image')
    news_form['image'] = img

    try:
      NewsService().create(news_form)
      return add_toast(make_response(), "success", _("News created successfully"))
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
    return make_response()
