from app.extensions import db
from datetime import datetime


class ClienteStarlink(db.Model):
    __tablename__ = "clientes_starlink"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    conta_starlink = db.Column(db.String(120), nullable=True)
    email_conta = db.Column(db.String(120), nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

    comissoes = db.relationship("ComissaoStarlink", backref="cliente_starlink", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClienteStarlink {self.conta_starlink}>"


class ComissaoStarlink(db.Model):
    __tablename__ = "comissoes_starlink"

    id = db.Column(db.Integer, primary_key=True)
    cliente_starlink_id = db.Column(db.Integer, db.ForeignKey("clientes_starlink.id"), nullable=False)
    data = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<ComissaoStarlink R${self.valor}>"
