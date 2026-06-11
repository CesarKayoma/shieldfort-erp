from app.extensions import db
from app.models.base import BaseModel
import enum



class StatusOrcamento(enum.Enum):
    RASCUNHO = "rascunho"
    ENVIADO = "enviado"
    APROVADO = "aprovado"
    RECUSADO = "recusado"


class Orcamento(BaseModel):
    __tablename__ = "orcamentos"

    
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True)
    status = db.Column(db.Enum(StatusOrcamento), nullable=False, default=StatusOrcamento.RASCUNHO)
    ativo = db.Column(db.Boolean, default=True)
    itens = db.relationship("ItemOrcamento", backref="orcamento", lazy=True, cascade="all, delete-orphan")
    venda = db.relationship("Venda", backref="orcamento", uselist=False)
    cliente = db.relationship("Cliente",backref="orcamentos")

    @property
    def total(self):    
        return sum(item.subtotal for item in self.itens)

    def __repr__(self):
        return f"<Orcamento {self.id} - {self.status}>"


class ItemOrcamento(BaseModel):
    __tablename__ = "itens_orcamento"

    id = db.Column(db.Integer, primary_key=True)
    orcamento_id = db.Column(db.Integer, db.ForeignKey("orcamentos.id"), unique=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True, index=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=True, index=True)
    descricao = db.Column(db.String(255), nullable=False)
    quantidade = db.Column(db.Float, nullable=False, default=1)
    preco_unitario = db.Column(db.Numeric(10,2), nullable=False, default=0)

    categoria = db.relationship("Categoria")

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __repr__(self):
        return f"<ItemOrcamento {self.descricao}>"
