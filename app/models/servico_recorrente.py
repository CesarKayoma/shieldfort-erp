from app.extensions import db
from datetime import datetime


class ServicoRecorrente(db.Model):
    __tablename__ = "servicos_recorrentes"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    valor_mensal = db.Column(db.Float, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    pagamentos = db.relationship("PagamentoMensal", backref="servico", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ServicoRecorrente {self.descricao}>"


class PagamentoMensal(db.Model):
    __tablename__ = "pagamentos_mensais"

    id = db.Column(db.Integer, primary_key=True)
    servico_recorrente_id = db.Column(db.Integer, db.ForeignKey("servicos_recorrentes.id"), nullable=False)
    mes_referencia = db.Column(db.String(7), nullable=False)  # formato: YYYY-MM
    data_pagamento = db.Column(db.Date, nullable=True)
    valor_pago = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default="pendente")  # pendente | pago

    def __repr__(self):
        return f"<PagamentoMensal {self.mes_referencia} - {self.status}>"
