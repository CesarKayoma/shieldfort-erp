from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

from app.models import CategoriaProduto, UnidadeMedida


class ProdutoForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    descricao = StringField("Descrição", validators=[DataRequired(), Length(max=255)])
    categoria_id = SelectField("Categoria", coerce=int, validators=[DataRequired()])
    unidade_medida_id = SelectField("Unidade de medida", coerce=int, validators=[DataRequired()])
    valor_padrao = DecimalField(
        "Valor padrão", places=2, default=Decimal("0.00"), validators=[Optional(), NumberRange(min=0)]
    )
    ativo = BooleanField("Ativo", default=True)
    submit = SubmitField("Salvar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categoria_id.choices = [
            (c.id, c.nome) for c in CategoriaProduto.query.order_by(CategoriaProduto.nome).all()
        ]
        self.unidade_medida_id.choices = [
            (u.id, f"{u.sigla} — {u.descricao}") for u in UnidadeMedida.query.order_by(UnidadeMedida.sigla).all()
        ]
