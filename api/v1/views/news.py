import json

from flask import make_response, render_template, request
from flask_babel import gettext as _
from marshmallow import ValidationError

from api.v1.views import bp
from app.services import NewsService
from utils.cache_mgr import cache_response, invalidate_cache
from utils.toast_notify import with_toast
from utils.view_modifiers import response

news_service = NewsService()


@bp.route("/dashboard/news/form", methods=["GET"])
@response(template_file="partials/dashboard/news-form.html")
def retrieve_form():
    """Get news form"""
    return dict()


@bp.route("/dashboard/news", methods=["GET"])
@response(template_file="partials/dashboard/news-list.html")
@cache_response()
def get_news():
    """Get news paginated"""
    page = request.args.get("page", type=int, default=1)
    news = news_service.get_all(page=page)
    data = news.get("data")
    del news["data"]
    return dict(data=data, **news)


@bp.route("/news/<id>", methods=["GET"])
@response(template_file="single-news.html")
@cache_response()
def get_single_news(id):
    """Get single news"""
    news = news_service.get_by_uuid(id)
    return dict(**news)


@bp.route("/dashboard/news", methods=["POST"])
@with_toast
@response(template_file="partials/dashboard/news.html")
def create_news():
    """Create news"""
    news_form = request.form.to_dict()
    img = request.files.get("image")
    news_form["image"] = img
    data = {}
    msg = ""
    err = False

    try:
        news = news_service.create(news_form)
        data = news_service.get_all()
        msg = "News created successfully"
    except ValidationError as e:
        err = True
        msg = str(e)
    except Exception as e:
        err = True
        msg = "Unexepected error occurred"

    if err:
        data = news_service.get_all()
    invalidate_cache(["news", "get_single_news", "get_news", "index"])
    return dict(**data, toast={"type": "error" if err else "success", "message": msg})


@bp.route("/dashboard/news/<news_id>", methods=["GET", "PUT", "PATCH"])
@response(template_file="partials/dashboard/news-form.html")
@with_toast
def update_news(news_id):
    """Update news"""
    news = news_service.get_by_uuid(news_id)
    if not news:
        return dict(toast={"type": "error", "message": "News not found"})
    if request.method == "PATCH" or request.method == "PUT":

        try:
            news_form = request.form.to_dict()
            news_service.update(news_id, news_form)
            resp = make_response(
                render_template(
                    "partials/dashboard/news.html", **news_service.get_all()
                )
            )
            resp.headers["hx-toast"] = json.dumps(
                {"type": "success", "message": "News updated successfully"}
            )
            return resp
        except ValidationError as e:
            resp = make_response(
                render_template(
                    "partials/dashboard/news.html", **news_service.get_all()
                )
            )
            resp.headers["hx-toast"] = json.dumps({"type": "error", "message": str(e)})
    invalidate_cache(["news", "get_single_news", "get_news", "index"])
    return dict(update=True, **news)


@bp.route("/dashboard/news/<news_id>", methods=["DELETE"])
@with_toast
def delete_news(news_id):
    """Delete news"""
    page = request.args.get("page", type=int, default=1)
    try:
        news_service.delete(news_id)
        custom_header = json.dumps(
            {"type": "success", "message": "News deleted successfully"}
        )
    except Exception as e:
        custom_header = json.dumps(
            {"type": "error", "message": "Unexpected error occurred"}
        )

    news = news_service.get_all(page=page)
    resp = make_response(render_template("partials/dashboard/news-list.html", **news))
    resp.headers["hx-toast"] = custom_header
    invalidate_cache(["news", "get_single_news", "get_news", "index"])
    return resp
