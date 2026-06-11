from app.extensions import db
from app.models.base import BaseModel


class Cliente(BaseModel):
    __tablename__ = "clientes"

    
    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(2), nullable=False, default="PF")  # PF ou PJ
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    endereco = db.Column(db.String(255), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    orcamentos = db.relationship("Orcamento", backref="cliente", lazy=True)

    def __repr__(self):
        return f"<Cliente {self.nome}>"
