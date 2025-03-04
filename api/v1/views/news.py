import json
from flask import make_response, render_template, request
from flask_babel import gettext as _
from marshmallow import ValidationError

from api.v1.views import bp
from app.services.news import NewsService
from utils.toast_notify import with_toast
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
@with_toast
def create_news():
    """Create news"""
    news_form = request.form.to_dict()
    img = request.files.get('image')
    news_form['image'] = img

    try:
        news = NewsService().create(news_form)
        return dict(
            toast={"type": "success", "message": "News created successfully"},
        )
    except ValidationError as e:
        return dict(
            toast={"type": "error", "message": str(e)}
        )
    except Exception as e:
        return dict(
            toast={"type": "error", "message": _("Unexpected error occurred")}
        )


@bp.route("/dashboard/news/<news_id>", methods=["GET", "PUT", "PATCH"])
@response(template_file="partials/dashboard/news-form.html")
@with_toast
def update_news(news_id):
    """Update news"""
    if request.method == "PATCH" or request.method == "PUT":
        news_form = request.form.to_dict()
        NewsService().update(news_id, news_form)
    return dict(update=True)


@bp.route("/dashboard/news/<news_id>", methods=["DELETE"])
@with_toast
def delete_news(news_id):
    """Delelte news"""
    page = request.args.get("page", type=int, default=1)
    news_service = NewsService()
    try:
        news_service.delete(news_id)
        custom_header = json.dumps({
          "type": "success",
          "message": "News deleted successfully"
        })
    except Exception as e:
        custom_header = json.dumps({
          "type": "error",
          "message": "Unexpected error occurred"
        })

    news = news_service.get_all(page=page)
    data = news.get('news')
    del news['news']
    resp = make_response(render_template("partials/dashboard/news-list.html",
                                      data=data, **news))
    resp.headers["hx-toast"] = custom_header
    return resp
