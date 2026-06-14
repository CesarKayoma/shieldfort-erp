from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, BooleanField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

from app.models import Orcamento
from app.models.orcamento import StatusOrcamento
from app.models.pagamento import FormaPagamento, FORMA_PAGAMENTO_LABELS
from app.models.servico import StatusServico, STATUS_SERVICO_LABELS


class ServicoForm(FlaskForm):
    orcamento_id = SelectField("Orçamento", coerce=int, validators=[DataRequired()])
    status = SelectField(
        "Status",
        choices=[(s.value, STATUS_SERVICO_LABELS[s]) for s in StatusServico],
        validators=[DataRequired()],
    )
    data_execucao = DateField("Data de execução", validators=[Optional()])
    observacoes = StringField("Observações", validators=[Optional(), Length(max=255)])
    ativo = BooleanField("Ativo", default=True)

    valor_servico = DecimalField(
        "Valor do serviço", places=2, validators=[DataRequired(), NumberRange(min=0.01)]
    )
    forma_pagamento = SelectField(
        "Forma de pagamento",
        choices=[(f.value, FORMA_PAGAMENTO_LABELS[f]) for f in FormaPagamento],
        validators=[DataRequired()],
    )
    numero_parcelas = IntegerField(
        "Número de parcelas", default=1, validators=[DataRequired(), NumberRange(min=1, max=48)]
    )
    data_primeira_parcela = DateField("Vencimento da 1ª parcela", validators=[DataRequired()])

    submit = SubmitField("Salvar")

    def __init__(self, *args, servico=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._servico = servico

        query = Orcamento.query.filter(Orcamento.status == StatusOrcamento.APROVADO)
        disponiveis = [o for o in query.all() if o.servico is None or (servico and o.id == servico.orcamento_id)]
        disponiveis.sort(key=lambda o: o.id, reverse=True)

        self.orcamento_id.choices = [
            (o.id, f"#{o.id} — {o.cliente.nome} (R$ {o.total:.2f})") for o in disponiveis
        ]
