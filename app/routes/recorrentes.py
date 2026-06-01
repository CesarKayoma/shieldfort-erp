from flask import Blueprint

bp = Blueprint("recorrentes", __name__)


@bp.route("/")
def index():
    return "recorrentes ok"