from flask import make_response, redirect, render_template, request, session, url_for, flash, render_template_string
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



@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page with HTMX"""
    # If it's a GET request, render the login page
    if request.method == "GET":
        return render_template("login.html")

    # Handle POST request (login attempt)
    username = request.form.get("username")
    password = request.form.get("password")
    # Dummy validation (replace with real auth logic)
    if not username or not password:
        return make_response("<p class='text-red-500'>Please enter both username and password to login.</p>", 400)

    if username != "a" or password != "a":
        return make_response("<p class='text-red-500'>Invalid credentials. Please try again.</p>", 400)

    # Successful login - Use HX-Redirect header for redirection
    response = make_response()
    response.headers["HX-Redirect"] = url_for('app_views.dashboard')
    return response


@bp.route("/dashboard")
@response(template_file="dashboard.html")
def dashboard():
    """Dashboard page"""
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
