from app.extensions import db
from app.models.base import BaseModel
from app.models.pagamento import FormaPagamento, StatusParcela
from datetime import date
from decimal import Decimal


class Gasto(BaseModel):
    __tablename__ = "gastos"

    descricao = db.Column(db.String(255), nullable=False)
    quantidade = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("1.00"))
    unidade_medida_id = db.Column(db.Integer, db.ForeignKey("unidades_medidas.id"), nullable=False, index=True)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    forma_pagamento = db.Column(
        db.Enum(
            FormaPagamento,
            name="forma_pagamento_gasto",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )

    unidade_medida = db.relationship("UnidadeMedida")

    parcelas = db.relationship(
        "ParcelaGasto",
        backref="gasto",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="ParcelaGasto.numero",
    )

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def __repr__(self):
        return f"<Gasto {self.descricao}>"


class ParcelaGasto(BaseModel):
    __tablename__ = "parcelas_gasto"

    gasto_id = db.Column(db.Integer, db.ForeignKey("gastos.id"), nullable=False, index=True)
    numero = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    status = db.Column(
        db.Enum(
            StatusParcela,
            name="status_parcela_gasto",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=StatusParcela.PENDENTE,
    )

    @property
    def esta_atrasada(self):
        return self.status == StatusParcela.PENDENTE and self.data_vencimento < date.today()

    def __repr__(self):
        return f"<ParcelaGasto {self.numero} - {self.status.value}>"
