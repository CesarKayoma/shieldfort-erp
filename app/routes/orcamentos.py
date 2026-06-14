from decimal import Decimal, InvalidOperation

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.forms.orcamento import OrcamentoForm
from app.services import orcamento_service
from app.models import Produto, CategoriaProduto
from app.models.orcamento import StatusOrcamento

bp = Blueprint("orcamentos", __name__)


@bp.route("/")
@login_required
def index():
    status = request.args.get("status", "").strip()
    page = request.args.get("page", 1, type=int)

    pagination = orcamento_service.listar_orcamentos(status=status, page=page)

    return render_template(
        "orcamentos/index.html",
        orcamentos=pagination.items,
        pagination=pagination,
        total=orcamento_service.contar_orcamentos(),
    )


@bp.route("/novo", methods=["GET", "POST"])
@login_required
def novo():
    form = OrcamentoForm()
    if form.validate_on_submit():
        itens_data, erro = _ler_itens(request.form)
        if erro:
            flash(erro, "danger")
        else:
            orcamento = orcamento_service.criar_orcamento(form, itens_data)
            flash("Orçamento criado com sucesso.", "success")
            return redirect(url_for("orcamentos.show", id=orcamento.id))
    return render_template(
        "orcamentos/form.html",
        form=form,
        orcamento=None,
        produtos=_produtos_json(),
        categorias=_categorias_json(),
        itens_existentes=[],
    )


@bp.route("/<int:id>")
@login_required
def show(id):
    orcamento = orcamento_service.obter_orcamento(id)
    transicoes = orcamento_service.TRANSICOES_VALIDAS.get(orcamento.status, [])
    return render_template("orcamentos/detail.html", orcamento=orcamento, transicoes=transicoes)


@bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    orcamento = orcamento_service.obter_orcamento(id)
    if orcamento.status != StatusOrcamento.RASCUNHO:
        flash("Apenas orçamentos em rascunho podem ser editados.", "danger")
        return redirect(url_for("orcamentos.show", id=id))

    form = OrcamentoForm(obj=orcamento)
    if form.validate_on_submit():
        itens_data, erro = _ler_itens(request.form)
        if erro:
            flash(erro, "danger")
        else:
            orcamento_service.atualizar_orcamento(orcamento, form, itens_data)
            flash("Orçamento atualizado com sucesso.", "success")
            return redirect(url_for("orcamentos.show", id=id))
    elif request.method == "GET":
        form.cliente_id.data = orcamento.cliente_id

    return render_template(
        "orcamentos/form.html",
        form=form,
        orcamento=orcamento,
        produtos=_produtos_json(),
        categorias=_categorias_json(),
        itens_existentes=_itens_json(orcamento),
    )


@bp.route("/<int:id>/excluir", methods=["POST"])
@login_required
def excluir(id):
    orcamento = orcamento_service.obter_orcamento(id)
    orcamento_service.excluir_orcamento(orcamento)
    flash("Orçamento removido com sucesso.", "success")
    return redirect(url_for("orcamentos.index"))


@bp.route("/<int:id>/status", methods=["POST"])
@login_required
def mudar_status(id):
    orcamento = orcamento_service.obter_orcamento(id)
    try:
        novo_status = StatusOrcamento(request.form.get("status"))
        orcamento_service.atualizar_status(orcamento, novo_status)
        flash("Status do orçamento atualizado.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("orcamentos.show", id=id))


def _ler_itens(form_data):
    produto_ids = form_data.getlist("item_produto_id")
    categoria_ids = form_data.getlist("item_categoria_id")
    descricoes = form_data.getlist("item_descricao")
    quantidades = form_data.getlist("item_quantidade")
    precos = form_data.getlist("item_preco_unitario")

    itens = []
    for i, descricao in enumerate(descricoes):
        descricao = descricao.strip()
        if not descricao:
            continue
        try:
            quantidade = Decimal(quantidades[i])
            preco_unitario = Decimal(precos[i])
            produto_id = int(produto_ids[i])
            categoria_id = int(categoria_ids[i])
        except (InvalidOperation, ValueError, IndexError):
            return None, "Dados de item inválidos."

        if quantidade <= 0 or preco_unitario < 0:
            return None, "Quantidade e preço unitário dos itens devem ser positivos."

        itens.append(
            {
                "produto_id": produto_id,
                "categoria_id": categoria_id,
                "descricao": descricao,
                "quantidade": quantidade,
                "preco_unitario": preco_unitario,
            }
        )

    if not itens:
        return None, "Adicione ao menos um item ao orçamento."
    return itens, None


def _produtos_json():
    return [
        {
            "id": p.id,
            "nome": p.nome,
            "descricao": p.descricao,
            "categoria_id": p.categoria_id,
            "valor_padrao": float(p.valor_padrao) if p.valor_padrao is not None else 0,
        }
        for p in Produto.query.order_by(Produto.nome).all()
    ]


def _categorias_json():
    return [{"id": c.id, "nome": c.nome} for c in CategoriaProduto.query.order_by(CategoriaProduto.nome).all()]


def _itens_json(orcamento):
    return [
        {
            "produto_id": item.produto_id,
            "categoria_id": item.categoria_id,
            "descricao": item.descricao,
            "quantidade": float(item.quantidade),
            "preco_unitario": float(item.preco_unitario),
        }
        for item in orcamento.itens
    ]
