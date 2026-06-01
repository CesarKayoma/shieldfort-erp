from app.extensions import db
from datetime import datetime


class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey("orcamentos.id"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    forma_pagamento = db.Column(db.String(20), nullable=True)  # pix | parcelado
    status_pagamento = db.Column(db.String(20), default="pendente")  # pendente | pago
    valor_total = db.Column(db.Float, nullable=False)

    instalacao = db.relationship("Instalacao", backref="venda", uselist=False)
    gastos = db.relationship("GastoInstalacao", backref="venda", lazy=True)

    def __repr__(self):
        return f"<Venda {self.id} - R${self.valor_total}>"
