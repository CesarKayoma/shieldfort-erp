from app.extensions import db
from datetime import datetime


class GastoInstalacao(db.Model):
    __tablename__ = "gastos_instalacao"

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=False)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f"<GastoInstalacao {self.descricao} - R${self.valor}>"
