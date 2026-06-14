from flask_wtf import FlaskForm
from wtforms import SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from app.models import Cliente


class OrcamentoForm(FlaskForm):
    cliente_id = SelectField("Cliente", coerce=int, validators=[DataRequired()])
    ativo = BooleanField("Ativo", default=True)
    submit = SubmitField("Salvar")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cliente_id.choices = [(c.id, c.nome) for c in Cliente.query.order_by(Cliente.nome).all()]
