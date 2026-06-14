from app.extensions import db
from app.models.base import BaseModel


class Produto(BaseModel):
    __tablename__ = "produtos"

    
    nome = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(255), nullable=False) 
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_produtos.id"), nullable=False )
    unidade_medida_id = db.Column(db.Integer, db.ForeignKey("unidades_medidas.id"), nullable=False )
    ativo = db.Column(db.Boolean, default=True)
    valor_padrao =  db.Column(db.Numeric(10, 2))

    categoria = db.relationship("CategoriaProduto")
    unidade_medida = db.relationship("UnidadeMedida")

    def __repr__(self):
        return f"<Produto {self.nome}>"


class CategoriaProduto(BaseModel):
    __tablename__ = "categorias_produtos"


    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)

class UnidadeMedida(BaseModel):
    __tablename__ = "unidades_medidas"

    sigla = db.Column(db.String(120), nullable=False)
    descricao = db.Column(db.String(255), nullable=False) 
