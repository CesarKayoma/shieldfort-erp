from app.extensions import db
from datetime import datetime


class Instalacao(db.Model):
    __tablename__ = "instalacoes"

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    data_realizacao = db.Column(db.DateTime, nullable=False)
    endereco = db.Column(db.String(255), nullable=True)
    tipo = db.Column(db.String(20), nullable=False, default="instalacao")  # instalacao | manutencao
    gratuita = db.Column(db.Boolean, default=False)
    observacoes = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime)

    cliente = db.relationship("Cliente", backref="instalacoes")

    def __repr__(self):
        return f"<Instalacao {self.id} - {self.tipo}>"
