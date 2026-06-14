from app.models import Cliente

def get_kpis():
    return {
        "total_clientes": Cliente.query.filter_by(ativo=True).count(),
        "instalacoes_mes": 0,   # implementar depois
        "faturamento_mes": "0,00",
        "vendas_mes": 0,
    }