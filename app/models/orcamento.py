from app.extensions import db
from datetime import datetime


class Orcamento(db.Model):
    __tablename__ = "orcamentos"

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="rascunho")
    # rascunho | enviado | aprovado | recusado
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    itens = db.relationship("ItemOrcamento", backref="orcamento", lazy=True, cascade="all, delete-orphan")
    venda = db.relationship("Venda", backref="orcamento", uselist=False)

    @property
    def total(self):
        return sum(item.subtotal for item in self.itens)

    def __repr__(self):
        return f"<Orcamento {self.id} - {self.status}>"


class ItemOrcamento(db.Model):
    __tablename__ = "itens_orcamento"

    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey("orcamentos.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    descricao = db.Column(db.String(255), nullable=False)
    quantidade = db.Column(db.Float, nullable=False, default=1)
    preco_unitario = db.Column(db.Float, nullable=False, default=0)

    categoria = db.relationship("Categoria")

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __repr__(self):
        return f"<ItemOrcamento {self.descricao}>"
