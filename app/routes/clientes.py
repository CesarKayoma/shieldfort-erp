from flask import Blueprint, render_template, request
from app.models import Cliente

bp = Blueprint("clientes", __name__)


@bp.route("/")
def index():
    return render_template("clientes/index.html")