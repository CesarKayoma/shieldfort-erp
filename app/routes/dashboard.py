from flask import Blueprint, render_template
from flask_login import login_required


bp = Blueprint("dashboard", __name__)

@bp.route("/")
@login_required
def index():
    return render_template("dashboard/index.html",
        kpis={
            "instalacoes_mes": 20,
            "faturamento_mes": "3.697,50",
            "total_clientes": 16,
            "vendas_mes": 18,
        },
        chart_instalacoes=[],
        proximos_servicos=[],
        ultimos_servicos=[],
        hoje="junho 2025"
    )