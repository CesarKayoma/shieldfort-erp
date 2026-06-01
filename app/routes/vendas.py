from flask import Blueprint

bp = Blueprint("vendas", __name__)


@bp.route("/")
def index():
    return "vendas ok"