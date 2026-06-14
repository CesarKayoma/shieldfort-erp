from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Produto

PER_PAGE = 10


def listar_produtos(q="", categoria_id="", page=1, per_page=PER_PAGE):
    query = Produto.query

    if q:
        query = query.filter(Produto.nome.ilike(f"%{q}%"))
    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)

    return query.order_by(Produto.nome).paginate(page=page, per_page=per_page)


def contar_produtos():
    return Produto.query.count()


def obter_produto(id):
    return Produto.query.get_or_404(id)


def criar_produto(form):
    produto = Produto()
    _aplicar_form(produto, form)
    db.session.add(produto)
    db.session.commit()
    return produto


def atualizar_produto(produto, form):
    _aplicar_form(produto, form)
    db.session.commit()
    return produto


def excluir_produto(produto):
    try:
        db.session.delete(produto)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def _aplicar_form(produto, form):
    produto.nome = form.nome.data.strip()
    produto.descricao = form.descricao.data.strip()
    produto.categoria_id = form.categoria_id.data
    produto.unidade_medida_id = form.unidade_medida_id.data
    produto.valor_padrao = form.valor_padrao.data
    produto.ativo = form.ativo.data
