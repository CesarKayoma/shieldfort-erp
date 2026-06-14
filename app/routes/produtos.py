from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.forms.produto import ProdutoForm
from app.services import produto_service
from app.models import CategoriaProduto

bp = Blueprint("produtos", __name__)


@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    categoria_id = request.args.get("categoria_id", "").strip()
    page = request.args.get("page", 1, type=int)

    pagination = produto_service.listar_produtos(q=q, categoria_id=categoria_id, page=page)

    return render_template(
        "produtos/index.html",
        produtos=pagination.items,
        pagination=pagination,
        total=produto_service.contar_produtos(),
        categorias=CategoriaProduto.query.order_by(CategoriaProduto.nome).all(),
    )


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = ProdutoForm()
    if form.validate_on_submit():
        produto_service.criar_produto(form)
        flash("Produto cadastrado com sucesso.", "success")
        return redirect(url_for("produtos.index"))
    return render_template("produtos/form.html", form=form, produto=None)


@bp.route("/<int:id>")
@login_required
def show(id):
    produto = produto_service.obter_produto(id)
    return render_template("produtos/detail.html", produto=produto)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    produto = produto_service.obter_produto(id)
    form = ProdutoForm(obj=produto)
    if form.validate_on_submit():
        produto_service.atualizar_produto(produto, form)
        flash("Produto atualizado com sucesso.", "success")
        return redirect(url_for("produtos.index"))
    return render_template("produtos/form.html", form=form, produto=produto)


@bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
def excluir(id):
    produto = produto_service.obter_produto(id)
    if produto_service.excluir_produto(produto):
        flash("Produto removido com sucesso.", "success")
    else:
        flash("Não é possível excluir este produto: ele está sendo usado em orçamentos.", "danger")
    return redirect(url_for("produtos.index"))
