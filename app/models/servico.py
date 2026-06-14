from app.extensions import db
from app.models.base import BaseModel
import enum


class StatusServico(enum.Enum):
    AGENDADO = "agendado"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


STATUS_SERVICO_LABELS = {
    StatusServico.AGENDADO: "Agendado",
    StatusServico.EM_ANDAMENTO: "Em andamento",
    StatusServico.CONCLUIDO: "Concluído",
    StatusServico.CANCELADO: "Cancelado",
}


class Servico(BaseModel):
    __tablename__ = "servicos"

    orcamento_id = db.Column(db.Integer, db.ForeignKey("orcamentos.id"), nullable=False, unique=True, index=True)
    status = db.Column(
        db.Enum(
            StatusServico,
            name="status_servico",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=StatusServico.AGENDADO,
    )
    data_execucao = db.Column(db.Date, nullable=True)
    observacoes = db.Column(db.String(255), nullable=True)
    ativo = db.Column(db.Boolean, default=True)

    orcamento = db.relationship("Orcamento", backref=db.backref("servico", uselist=False))
    pagamento = db.relationship("Pagamento", backref="servico", uselist=False, cascade="all, delete-orphan")

    @property
    def cliente(self):
        return self.orcamento.cliente

    def __repr__(self):
        return f"<Servico {self.id} - {self.status.value}>"
