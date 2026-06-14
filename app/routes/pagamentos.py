from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.models import Parcela
from app.services import pagamento_service

bp = Blueprint("pagamentos", __name__)


@bp.route("/")
@login_required
def index():
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    pagination = pagamento_service.listar_pagamentos(status=status, page=page)

    return render_template(
        "pagamentos/index.html",
        pagamentos=pagination.items,
        pagination=pagination,
        total=pagamento_service.contar_pagamentos(),
    )


@bp.route("/<int:id>")
@login_required
def show(id):
    pagamento = pagamento_service.obter_pagamento(id)
    return render_template("pagamentos/detail.html", pagamento=pagamento)


@bp.route("/<int:id>/parcelas/<int:parcela_id>/pagar", methods=["POST"])
@login_required
def pagar_parcela(id, parcela_id):
    parcela = Parcela.query.filter_by(id=parcela_id, pagamento_id=id).first_or_404()
    pagamento_service.marcar_parcela_paga(parcela, datetime.now(timezone.utc).date())
    flash("Parcela marcada como paga.", "success")
    return redirect(url_for("pagamentos.show", id=id))


@bp.route("/<int:id>/parcelas/<int:parcela_id>/desfazer", methods=["POST"])
@login_required
def desfazer_parcela(id, parcela_id):
    parcela = Parcela.query.filter_by(id=parcela_id, pagamento_id=id).first_or_404()
    pagamento_service.desmarcar_parcela_paga(parcela)
    flash("Parcela marcada como pendente.", "success")
    return redirect(url_for("pagamentos.show", id=id))
