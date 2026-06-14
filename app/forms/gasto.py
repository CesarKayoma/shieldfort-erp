from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

from app.models import UnidadeMedida
from app.models.pagamento import FormaPagamento, FORMA_PAGAMENTO_LABELS


class GastoForm(FlaskForm):
    descricao = StringField("Descrição", validators=[DataRequired(), Length(max=255)])
    quantidade = DecimalField(
        "Quantidade", places=2, default=Decimal("1.00"), validators=[DataRequired(), NumberRange(min=0.01)]
    )
    unidade_medida_id = SelectField("Unidade de medida", coerce=int, validators=[DataRequired()])
    valor_unitario = DecimalField(
        "Valor unitário", places=2, validators=[DataRequired(), NumberRange(min=0)]
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unidade_medida_id.choices = [
            (u.id, f"{u.sigla} — {u.descricao}") for u in UnidadeMedida.query.order_by(UnidadeMedida.sigla).all()
        ]
