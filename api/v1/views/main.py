from flask import make_response, redirect, render_template, request, session
from api.v1.views import bp
from config import Config
from utils.view_modifiers import response
from flask_babel import gettext as _

@bp.route("/")
@response(template_file="index.html")
def index():
    '''home page'''
    return dict()

@bp.route("/projects")
@response(template_file="projects.html")
def projects():
    '''projects page'''
    return dict()

@bp.route("/knowledge-hub")
@response(template_file="knowledge-hub.html")
def knowledge_hup():
    '''knowledge-hub page'''
    if request.headers.get("hx-tab"):
        return make_response(
                render_template(
                    "partials/research.html",
                    tab=request.args.get('q', 'research'))
                )
    return dict(tab='research')

@bp.route("/set_language")
def set_language():
    '''set language'''
    lang = request.args.get("lang")

    if lang and lang in Config.BABEL_SUPPORTED_LOCALES:
        session["lang"] = lang

    return redirect(request.referrer)
