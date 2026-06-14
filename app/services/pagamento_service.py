from app.extensions import db
from app.models.pagamento import Pagamento, Parcela, StatusParcela
from app.services.parcelamento import gerar_parcelas

PER_PAGE = 10


def listar_pagamentos(status="", page=1, per_page=PER_PAGE):
    query = Pagamento.query
    if status == "pendente":
        query = query.filter(Pagamento.parcelas.any(Parcela.status != StatusParcela.PAGO))
    elif status == "quitado":
        query = query.filter(~Pagamento.parcelas.any(Parcela.status != StatusParcela.PAGO))
    return query.order_by(Pagamento.criado_em.desc()).paginate(page=page, per_page=per_page)


def contar_pagamentos():
    return Pagamento.query.count()


def obter_pagamento(id):
    return Pagamento.query.get_or_404(id)


def aplicar_pagamento(servico, valor_total, forma_pagamento, numero_parcelas, data_primeira_parcela):
    if servico.pagamento is None:
        servico.pagamento = Pagamento(forma_pagamento=forma_pagamento, valor_total=valor_total)
    else:
        servico.pagamento.forma_pagamento = forma_pagamento
        servico.pagamento.valor_total = valor_total
        servico.pagamento.parcelas.clear()

    servico.pagamento.parcelas.extend(
        gerar_parcelas(Parcela, forma_pagamento, valor_total, numero_parcelas, data_primeira_parcela)
    )


def marcar_parcela_paga(parcela, data_pagamento):
    parcela.status = StatusParcela.PAGO
    parcela.data_pagamento = data_pagamento
    db.session.commit()


def desmarcar_parcela_paga(parcela):
    parcela.status = StatusParcela.PENDENTE
    parcela.data_pagamento = None
    db.session.commit()
