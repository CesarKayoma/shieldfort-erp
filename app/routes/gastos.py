from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.forms.gasto import GastoForm
from app.services import gasto_service
from app.models import ParcelaGasto

bp = Blueprint("gastos", __name__)


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    pagination = gasto_service.listar_gastos(q=q, page=page)

    return render_template(
        "gastos/index.html",
        gastos=pagination.items,
        pagination=pagination,
        total=gasto_service.contar_gastos(),
    )


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = GastoForm()
    if form.validate_on_submit():
        gasto_service.criar_gasto(form)
        flash("Gasto cadastrado com sucesso.", "success")
        return redirect(url_for("gastos.index"))
    return render_template("gastos/form.html", form=form, gasto=None)


@bp.route("/<int:id>")
@login_required
def show(id):
    gasto = gasto_service.obter_gasto(id)
    return render_template("gastos/detail.html", gasto=gasto)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    gasto = gasto_service.obter_gasto(id)
    form = GastoForm(obj=gasto)
    if form.validate_on_submit():
        gasto_service.atualizar_gasto(gasto, form)
        flash("Gasto atualizado com sucesso.", "success")
        return redirect(url_for("gastos.index"))
    if request.method == "GET":
        form.forma_pagamento.data = gasto.forma_pagamento.value
        if gasto.parcelas:
            form.numero_parcelas.data = len(gasto.parcelas)
            form.data_primeira_parcela.data = gasto.parcelas[0].data_vencimento
    return render_template("gastos/form.html", form=form, gasto=gasto)


@bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
def excluir(id):
    gasto = gasto_service.obter_gasto(id)
    gasto_service.excluir_gasto(gasto)
    flash("Gasto removido com sucesso.", "success")
    return redirect(url_for("gastos.index"))


@bp.route("/<int:id>/parcelas/<int:parcela_id>/pagar", methods=["POST"])
@login_required
def pagar_parcela(id, parcela_id):
    parcela = ParcelaGasto.query.filter_by(id=parcela_id, gasto_id=id).first_or_404()
    gasto_service.marcar_parcela_paga(parcela, datetime.now(timezone.utc).date())
    flash("Parcela marcada como paga.", "success")
    return redirect(url_for("gastos.show", id=id))
