import calendar
from decimal import Decimal, ROUND_HALF_UP

from app.models.pagamento import FormaPagamento, StatusParcela


def gerar_parcelas(parcela_cls, forma_pagamento, valor_total, numero_parcelas, data_primeira_parcela):
    """Gera as parcelas de um pagamento, seguindo a RN03 (cartão de crédito
    permite N parcelas; demais formas são sempre 1x)."""
    n = numero_parcelas if forma_pagamento == FormaPagamento.CARTAO_CREDITO else 1
    valor_parcela = (valor_total / n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    soma_parcelas_anteriores = valor_parcela * (n - 1)

    parcelas = []
    for numero in range(1, n + 1):
        valor = valor_parcela if numero < n else (valor_total - soma_parcelas_anteriores)
        parcelas.append(
            parcela_cls(
                numero=numero,
                valor=valor,
                data_vencimento=somar_meses(data_primeira_parcela, numero - 1),
                status=StatusParcela.PENDENTE,
            )
        )
    return parcelas


def somar_meses(data, meses):
    mes_total = data.month - 1 + meses
    ano = data.year + mes_total // 12
    mes = mes_total % 12 + 1
    dia = min(data.day, calendar.monthrange(ano, mes)[1])
    return data.replace(year=ano, month=mes, day=dia)
