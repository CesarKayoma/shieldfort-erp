from app.extensions import db
from app.models.base import BaseModel
import enum
from decimal import Decimal


class FormaPagamento(enum.Enum):
    PIX = "pix"
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    BOLETO = "boleto"
    DINHEIRO = "dinheiro"
    TRANSFERENCIA = "transferencia"


class StatusParcela(enum.Enum):
    PENDENTE = "pendente"
    PAGO = "pago"
    ATRASADO = "atrasado"


FORMA_PAGAMENTO_LABELS = {
    FormaPagamento.PIX: "PIX",
    FormaPagamento.CARTAO_CREDITO: "Cartão de Crédito",
    FormaPagamento.CARTAO_DEBITO: "Cartão de Débito",
    FormaPagamento.BOLETO: "Boleto",
    FormaPagamento.DINHEIRO: "Dinheiro",
    FormaPagamento.TRANSFERENCIA: "Transferência",
}


class Pagamento(BaseModel):
    __tablename__ = "pagamentos"

    servico_id = db.Column(db.Integer, db.ForeignKey("servicos.id"), nullable=False, unique=True, index=True)
    forma_pagamento = db.Column(
        db.Enum(
            FormaPagamento,
            name="forma_pagamento",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    parcelas = db.relationship(
        "Parcela",
        backref="pagamento",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Parcela.numero",
    )

    @property
    def quitado(self):
        return all(parcela.status == StatusParcela.PAGO for parcela in self.parcelas)

    def __repr__(self):
        return f"<Pagamento {self.id} - {self.forma_pagamento.value}>"


class Parcela(BaseModel):
    __tablename__ = "parcelas_pagamento"

    pagamento_id = db.Column(db.Integer, db.ForeignKey("pagamentos.id"), nullable=False, index=True)
    numero = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date, nullable=True)
    status = db.Column(
        db.Enum(
            StatusParcela,
            name="status_parcela",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=StatusParcela.PENDENTE,
    )

    def __repr__(self):
        return f"<Parcela {self.numero} - {self.status.value}>"
