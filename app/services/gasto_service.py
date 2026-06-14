import calendar
from decimal import Decimal, ROUND_HALF_UP

from app.extensions import db
from app.models import Gasto, ParcelaGasto
from app.models.pagamento import FormaPagamento, StatusParcela

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


def _aplicar_form(gasto, form):
    gasto.descricao = form.descricao.data.strip()
    gasto.quantidade = form.quantidade.data
    gasto.unidade_medida_id = form.unidade_medida_id.data
    gasto.valor_unitario = form.valor_unitario.data
    gasto.forma_pagamento = FormaPagamento(form.forma_pagamento.data)


def _gerar_parcelas(gasto, form):
    numero_parcelas = form.numero_parcelas.data if gasto.forma_pagamento == FormaPagamento.CARTAO_CREDITO else 1
    valor_total = gasto.valor_total
    valor_parcela = (valor_total / numero_parcelas).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    soma_parcelas_anteriores = valor_parcela * (numero_parcelas - 1)
    data_vencimento = form.data_primeira_parcela.data

    for numero in range(1, numero_parcelas + 1):
        valor = valor_parcela if numero < numero_parcelas else (valor_total - soma_parcelas_anteriores)
        gasto.parcelas.append(
            ParcelaGasto(
                numero=numero,
                valor=valor,
                data_vencimento=_somar_meses(data_vencimento, numero - 1),
                status=StatusParcela.PENDENTE,
            )
        )


def _somar_meses(data, meses):
    mes_total = data.month - 1 + meses
    ano = data.year + mes_total // 12
    mes = mes_total % 12 + 1
    dia = min(data.day, _ultimo_dia_do_mes(ano, mes))
    return data.replace(year=ano, month=mes, day=dia)


def _ultimo_dia_do_mes(ano, mes):
    return calendar.monthrange(ano, mes)[1]
