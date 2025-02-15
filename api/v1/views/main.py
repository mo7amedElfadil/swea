from flask import make_response, redirect, render_template, request, session, url_for, flash, render_template_string
from api.v1.views import bp
from config import Config
from utils.view_modifiers import response
from flask_babel import gettext as _

@bp.route("/")
@response(template_file="index.html")
def index():
    '''home page'''
    return dict(user="Mohamed Elfadil")

@bp.route("/projects")
@response(template_file="projects.html")
def projects():
    '''projects page'''
    return {"user" : "John Doe"}



@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page with HTMX"""
    # If it's a GET request, render the login page
    if request.method == "GET":
        return render_template("login.html")

    # Handle POST request (login attempt)
    username = request.form.get("username")
    password = request.form.get("password")
    print(username, password)
    # Dummy validation (replace with real auth logic)
    if username != "a" or password != "a":
        return "<p class='text-red-500'>Invalid credentials. Please try again.</p>", 400

    # Successful login - Use HX-Redirect header for redirection
    response = make_response()
    response.headers["HX-Redirect"] = url_for('app_views.dashboard')
    return response


@bp.route("/set_language")
def set_language():
    '''set language'''
    lang = request.args.get("lang")

    if lang and lang in Config.BABEL_SUPPORTED_LOCALES:
        session["lang"] = lang

    # TODO: should render the template conrresponding to the current page
    #return make_response(render_template("index.html"))
    return redirect(request.referrer)
