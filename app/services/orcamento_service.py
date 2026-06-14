from app.extensions import db
from app.models import Orcamento, ItemOrcamento
from app.models.orcamento import StatusOrcamento

PER_PAGE = 10

TRANSICOES_VALIDAS = {
    StatusOrcamento.RASCUNHO: [StatusOrcamento.ENVIADO, StatusOrcamento.RECUSADO],
    StatusOrcamento.ENVIADO: [StatusOrcamento.APROVADO, StatusOrcamento.RECUSADO],
    StatusOrcamento.APROVADO: [],
    StatusOrcamento.RECUSADO: [],
}


def listar_orcamentos(status="", page=1, per_page=PER_PAGE):
    query = Orcamento.query
    if status:
        query = query.filter(Orcamento.status == StatusOrcamento(status))
    return query.order_by(Orcamento.criado_em.desc()).paginate(page=page, per_page=per_page)


def contar_orcamentos():
    return Orcamento.query.count()


def obter_orcamento(id):
    return Orcamento.query.get_or_404(id)


def criar_orcamento(form, itens_data):
    orcamento = Orcamento()
    _aplicar_form(orcamento, form)
    _aplicar_itens(orcamento, itens_data)
    db.session.add(orcamento)
    db.session.commit()
    return orcamento


def atualizar_orcamento(orcamento, form, itens_data):
    _aplicar_form(orcamento, form)
    orcamento.itens.clear()
    _aplicar_itens(orcamento, itens_data)
    db.session.commit()
    return orcamento


def excluir_orcamento(orcamento):
    db.session.delete(orcamento)
    db.session.commit()


def atualizar_status(orcamento, novo_status):
    permitidos = TRANSICOES_VALIDAS.get(orcamento.status, [])
    if novo_status not in permitidos:
        raise ValueError(
            f"Não é possível mudar de '{orcamento.status.value}' para '{novo_status.value}'."
        )
    orcamento.status = novo_status
    db.session.commit()
    return orcamento


def _aplicar_form(orcamento, form):
    orcamento.cliente_id = form.cliente_id.data
    orcamento.ativo = form.ativo.data


def _aplicar_itens(orcamento, itens_data):
    for item in itens_data:
        orcamento.itens.append(
            ItemOrcamento(
                produto_id=item["produto_id"],
                categoria_id=item["categoria_id"],
                descricao=item["descricao"],
                quantidade=item["quantidade"],
                preco_unitario=item["preco_unitario"],
            )
        )
