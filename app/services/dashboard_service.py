import calendar
from datetime import date, timedelta
from decimal import Decimal

from app.extensions import db
from app.models import Cliente, Orcamento, Servico
from app.models.gasto import ParcelaGasto
from app.models.orcamento import StatusOrcamento
from app.models.pagamento import Parcela, StatusParcela
from app.models.servico import StatusServico


def get_kpis():
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    fim_mes = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

    servicos_concluidos_mes = Servico.query.filter(
        Servico.status == StatusServico.CONCLUIDO,
        Servico.data_execucao >= inicio_mes,
        Servico.data_execucao <= fim_mes,
    ).all()

    faturamento_mes = sum(
        (s.pagamento.valor_total for s in servicos_concluidos_mes if s.pagamento),
        Decimal("0.00"),
    )

    vendas_mes = Servico.query.filter(
        db.func.date(Servico.criado_em) >= inicio_mes,
        db.func.date(Servico.criado_em) <= fim_mes,
    ).count()

    return {
        "total_clientes": Cliente.query.filter_by(ativo=True).count(),
        "instalacoes_mes": len(servicos_concluidos_mes),
        "faturamento_mes": faturamento_mes,
        "vendas_mes": vendas_mes,
    }


def get_financeiro():
    hoje = date.today()
    inicio_mes = hoje.replace(day=1)
    fim_mes = hoje.replace(day=calendar.monthrange(hoje.year, hoje.month)[1])

    parcelas_receber = Parcela.query.filter(Parcela.status != StatusParcela.PAGO).all()
    parcelas_pagar = ParcelaGasto.query.filter(ParcelaGasto.status != StatusParcela.PAGO).all()

    atrasadas = []
    for parcela in parcelas_receber:
        if parcela.esta_atrasada:
            atrasadas.append({
                "tipo": "receber",
                "descricao": parcela.pagamento.servico.cliente.nome,
                "valor": parcela.valor,
                "data_vencimento": parcela.data_vencimento,
                "pagamento_id": parcela.pagamento_id,
            })
    for parcela in parcelas_pagar:
        if parcela.esta_atrasada:
            atrasadas.append({
                "tipo": "pagar",
                "descricao": parcela.gasto.descricao,
                "valor": parcela.valor,
                "data_vencimento": parcela.data_vencimento,
                "gasto_id": parcela.gasto_id,
            })
    atrasadas.sort(key=lambda item: item["data_vencimento"])

    return {
        "a_receber_total": sum((p.valor for p in parcelas_receber), Decimal("0.00")),
        "a_pagar_total": sum((p.valor for p in parcelas_pagar), Decimal("0.00")),
        "saldo_previsto_mes": (
            sum((p.valor for p in parcelas_receber if inicio_mes <= p.data_vencimento <= fim_mes), Decimal("0.00"))
            - sum((p.valor for p in parcelas_pagar if inicio_mes <= p.data_vencimento <= fim_mes), Decimal("0.00"))
        ),
        "atrasadas": atrasadas,
    }


def get_agenda():
    hoje = date.today()
    limite = hoje + timedelta(days=7)

    proximos_servicos = (
        Servico.query
        .filter(Servico.status.in_([StatusServico.AGENDADO, StatusServico.EM_ANDAMENTO]))
        .filter(Servico.data_execucao.isnot(None))
        .filter(Servico.data_execucao >= hoje)
        .filter(Servico.data_execucao <= limite)
        .order_by(Servico.data_execucao.asc())
        .limit(5)
        .all()
    )

    return {
        "proximos_servicos": proximos_servicos,
        "orcamentos_pendentes": Orcamento.query.filter(Orcamento.status == StatusOrcamento.ENVIADO).count(),
    }
