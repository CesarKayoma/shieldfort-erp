from flask import Blueprint

bp = Blueprint("gastos", __name__)


@bp.route("/")
def index():
    return "gastos ok"
