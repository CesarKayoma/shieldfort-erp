from flask import Blueprint

bp = Blueprint("instalacoes", __name__)


@bp.route("/")
def index():
    return "instalacoes ok"
