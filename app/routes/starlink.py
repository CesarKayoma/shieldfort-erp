from flask import Blueprint

bp = Blueprint("starlink", __name__)


@bp.route("/")
def index():
    return "starlink ok"
