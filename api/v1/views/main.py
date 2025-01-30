from api.v1.views import bp

@bp.route("/", methods=["GET", "POST"])
def index():
    return "Hello, World!"
