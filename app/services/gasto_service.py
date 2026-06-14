from app.extensions import db
from app.models import Gasto, ParcelaGasto
from app.models.pagamento import FormaPagamento, StatusParcela
from app.services.parcelamento import gerar_parcelas

PER_PAGE = 10


def listar_gastos(q="", page=1, per_page=PER_PAGE):
    query = Gasto.query
    if q:
        query = query.filter(Gasto.descricao.ilike(f"%{q}%"))
    return query.order_by(Gasto.criado_em.desc()).paginate(page=page, per_page=per_page)


def contar_gastos():
    return Gasto.query.count()


def obter_gasto(id):
    return Gasto.query.get_or_404(id)


def criar_gasto(form):
    gasto = Gasto()
    _aplicar_form(gasto, form)
    _gerar_parcelas(gasto, form)
    db.session.add(gasto)
    db.session.commit()
    return gasto


def atualizar_gasto(gasto, form):
    _aplicar_form(gasto, form)
    gasto.parcelas.clear()
    _gerar_parcelas(gasto, form)
    db.session.commit()
    return gasto


def excluir_gasto(gasto):
    db.session.delete(gasto)
    db.session.commit()


def marcar_parcela_paga(parcela, data_pagamento):
    parcela.status = StatusParcela.PAGO
    parcela.data_pagamento = data_pagamento
    db.session.commit()


def desmarcar_parcela_paga(parcela):
    parcela.status = StatusParcela.PENDENTE
    parcela.data_pagamento = None
    db.session.commit()


def _aplicar_form(gasto, form):
    gasto.descricao = form.descricao.data.strip()
    gasto.quantidade = form.quantidade.data
    gasto.unidade_medida_id = form.unidade_medida_id.data
    gasto.valor_unitario = form.valor_unitario.data
    gasto.forma_pagamento = FormaPagamento(form.forma_pagamento.data)


def _gerar_parcelas(gasto, form):
    gasto.parcelas.extend(
        gerar_parcelas(
            ParcelaGasto,
            gasto.forma_pagamento,
            gasto.valor_total,
            form.numero_parcelas.data,
            form.data_primeira_parcela.data,
        )
    )
