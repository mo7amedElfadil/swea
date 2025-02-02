from flask import make_response, render_template, request, session
from api.v1.views import bp
from config import Config
from utils.view_modifiers import response

@bp.route("/")
@response(template_file="index.html")
def index():
    '''home page'''
    if request.headers.get("hx-request"):
        html = '<h2> this markup from backend, open network tab</h2>'
        return make_response(html)
    return {"user" : "John Doe"}

@bp.route("/projects")
@response(template_file="projects.html")
def projects():
    '''projects page'''
    return {"user" : "John Doe"}

@bp.route("/set_language")
def set_language():
    '''set language'''
    lang = request.args.get("lang")

    if lang and lang in Config.BABEL_SUPPORTED_LOCALES:
        session["lang"] = lang

    # TODO: should render the template conrresponding to the current page

    return make_response(render_template("index.html"))
