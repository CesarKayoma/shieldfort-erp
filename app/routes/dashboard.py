from flask import Blueprint, render_template
from flask_login import login_required
from app.services.dashboard_service import get_kpis

bp = Blueprint("dashboard", __name__)

@bp.route("/")
@login_required
def index():
    return render_template("dashboard/index.html",
        kpis=get_kpis(),
        chart_instalacoes=[],
        proximos_servicos=[],
        ultimos_servicos=[],
        hoje="junho 2025"
    )