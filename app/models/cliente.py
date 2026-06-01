from app.extensions import db
from datetime import datetime


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(2), nullable=False, default="PF")  # PF ou PJ
    cpf_cnpj = db.Column(db.String(20), unique=True, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    endereco = db.Column(db.String(255), nullable=True)
    tem_mensalidade = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    orcamentos = db.relationship("Orcamento", backref="cliente", lazy=True)
    vendas = db.relationship("Venda", backref="cliente", lazy=True)
    servicos_recorrentes = db.relationship("ServicoRecorrente", backref="cliente", lazy=True)
    starlink = db.relationship("ClienteStarlink", backref="cliente", uselist=False)

    def __repr__(self):
        return f"<Cliente {self.nome}>"
