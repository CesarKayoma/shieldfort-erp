from app.extensions import db
from app.models.base import BaseModel
import enum
from decimal import Decimal



class StatusOrcamento(enum.Enum):
    RASCUNHO = "rascunho"
    ENVIADO = "enviado"
    APROVADO = "aprovado"
    RECUSADO = "recusado"


class Orcamento(BaseModel):
    __tablename__ = "orcamentos"

    
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False, index=True)
    status = db.Column(db.Enum(StatusOrcamento, name="status_orcamento"), nullable=False, default=StatusOrcamento.RASCUNHO)
    ativo = db.Column(db.Boolean, default=True)
    itens = db.relationship("ItemOrcamento", backref="orcamento", lazy=True, cascade="all, delete-orphan")

    @property
    def total(self):    
        return sum(item.subtotal for item in self.itens)

    def __repr__(self):
        return f"<Orcamento {self.id} - {self.status.value}>"


class ItemOrcamento(BaseModel):
    __tablename__ = "itens_orcamento"

    orcamento_id = db.Column(db.Integer, db.ForeignKey("orcamentos.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_produtos.id"), nullable=True, index=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=True, index=True)
    descricao = db.Column(db.String(255), nullable=False)
    quantidade = db.Column(db.Numeric(10,2),nullable=False,default=Decimal("1.00"))
    preco_unitario = db.Column(db.Numeric(10,2), nullable=False, default=Decimal("0.00"))

    categoria = db.relationship("CategoriaProduto")

    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __repr__(self):
        return f"<ItemOrcamento {self.descricao}>"
