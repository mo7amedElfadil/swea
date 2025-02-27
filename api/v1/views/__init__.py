"""Module instantiates Blueprint for all the views"""

from flask import Blueprint

bp = Blueprint("app_views", __name__, template_folder="templates")

from api.v1.views.main import *
from api.v1.views.news import *
from api.v1.views.projects import *
from api.v1.views.team import *
