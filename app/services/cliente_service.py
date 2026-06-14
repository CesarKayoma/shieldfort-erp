from app.extensions import db
from app.models import Cliente

PER_PAGE = 10


def listar_clientes(q="", tipo="", page=1, per_page=PER_PAGE):
    query = Cliente.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            db.or_(
                Cliente.nome.ilike(like),
                Cliente.cpf_cnpj.ilike(like),
                Cliente.telefone.ilike(like),
            )
        )
    if tipo:
        query = query.filter(Cliente.tipo == tipo)

    return query.order_by(Cliente.nome).paginate(page=page, per_page=per_page)


def contar_clientes():
    return Cliente.query.count()


def obter_cliente(id):
    return Cliente.query.get_or_404(id)


def criar_cliente(form):
    cliente = Cliente()
    _aplicar_form(cliente, form)
    db.session.add(cliente)
    db.session.commit()
    return cliente


def atualizar_cliente(cliente, form):
    _aplicar_form(cliente, form)
    db.session.commit()
    return cliente


def excluir_cliente(cliente):
    db.session.delete(cliente)
    db.session.commit()


def _aplicar_form(cliente, form):
    cliente.nome = form.nome.data.strip()
    cliente.tipo = form.tipo.data
    cliente.cpf_cnpj = (form.cpf_cnpj.data or "").strip() or None
    cliente.telefone = (form.telefone.data or "").strip() or None
    cliente.email = (form.email.data or "").strip() or None
    cliente.endereco = (form.endereco.data or "").strip() or None
    cliente.ativo = form.ativo.data
