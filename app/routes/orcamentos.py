from flask import Blueprint

bp = Blueprint("orcamentos", __name__)


@bp.route("/")
def index():
    return "orcamentos ok"
