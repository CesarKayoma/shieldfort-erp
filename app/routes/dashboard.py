from datetime import date

from flask import Blueprint, render_template
from flask_login import login_required
from app.services.dashboard_service import get_agenda, get_financeiro, get_kpis

bp = Blueprint("dashboard", __name__)

MESES_PT = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]

@bp.route("/")
@login_required
def index():
    hoje = date.today()
    return render_template("dashboard/index.html",
        kpis=get_kpis(),
        financeiro=get_financeiro(),
        agenda=get_agenda(),
        hoje=f"{MESES_PT[hoje.month - 1]} {hoje.year}"
    )