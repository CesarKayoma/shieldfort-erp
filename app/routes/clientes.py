from flask import Blueprint

bp = Blueprint("clientes", __name__)


@bp.route("/")
def index():
    return "clientes ok"
