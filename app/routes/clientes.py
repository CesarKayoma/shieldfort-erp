from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.forms.cliente import ClienteForm
from app.services import cliente_service

bp = Blueprint("clientes", __name__)


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    tipo = request.args.get("tipo", "").strip()
    page = request.args.get("page", 1, type=int)

    pagination = cliente_service.listar_clientes(q=q, tipo=tipo, page=page)

    return render_template(
        "clientes/index.html",
        clientes=pagination.items,
        pagination=pagination,
        total=cliente_service.contar_clientes(),
    )


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = ClienteForm()
    if form.validate_on_submit():
        cliente_service.criar_cliente(form)
        flash("Cliente cadastrado com sucesso.", "success")
        return redirect(url_for("clientes.index"))
    return render_template("clientes/form.html", form=form, cliente=None)


@bp.route("/<int:id>")
@login_required
def show(id):
    cliente = cliente_service.obter_cliente(id)
    return render_template("clientes/detail.html", cliente=cliente)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    cliente = cliente_service.obter_cliente(id)
    form = ClienteForm(obj=cliente, cliente=cliente)
    if form.validate_on_submit():
        cliente_service.atualizar_cliente(cliente, form)
        flash("Cliente atualizado com sucesso.", "success")
        return redirect(url_for("clientes.index"))
    return render_template("clientes/form.html", form=form, cliente=cliente)


@bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
def excluir(id):
    cliente = cliente_service.obter_cliente(id)
    cliente_service.excluir_cliente(cliente)
    flash("Cliente removido com sucesso.", "success")
    return redirect(url_for("clientes.index"))
