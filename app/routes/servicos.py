from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.forms.servico import ServicoForm
from app.services import servico_service

bp = Blueprint("servicos", __name__)


@bp.route("/")
@login_required
def index():
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    pagination = servico_service.listar_servicos(status=status, page=page)

    return render_template(
        "servicos/index.html",
        servicos=pagination.items,
        pagination=pagination,
        total=servico_service.contar_servicos(),
    )


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = ServicoForm()
    if form.validate_on_submit():
        servico = servico_service.criar_servico(form)
        flash("Serviço cadastrado com sucesso.", "success")
        return redirect(url_for("servicos.show", id=servico.id))
    return render_template("servicos/form.html", form=form, servico=None)


@bp.route("/<int:id>")
@login_required
def show(id):
    servico = servico_service.obter_servico(id)
    return render_template("servicos/detail.html", servico=servico)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    servico = servico_service.obter_servico(id)
    form = ServicoForm(obj=servico, servico=servico)
    if form.validate_on_submit():
        servico_service.atualizar_servico(servico, form)
        flash("Serviço atualizado com sucesso.", "success")
        return redirect(url_for("servicos.show", id=id))
    if request.method == "GET":
        form.orcamento_id.data = servico.orcamento_id
        form.status.data = servico.status.value
        if servico.pagamento:
            form.valor_servico.data = servico.pagamento.valor_total
            form.forma_pagamento.data = servico.pagamento.forma_pagamento.value
            if servico.pagamento.parcelas:
                form.numero_parcelas.data = len(servico.pagamento.parcelas)
                form.data_primeira_parcela.data = servico.pagamento.parcelas[0].data_vencimento
    return render_template("servicos/form.html", form=form, servico=servico)


@bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
def excluir(id):
    servico = servico_service.obter_servico(id)
    servico_service.excluir_servico(servico)
    flash("Serviço removido com sucesso.", "success")
    return redirect(url_for("servicos.index"))
