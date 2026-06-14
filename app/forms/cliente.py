from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, Email, Length, ValidationError

from app.models import Cliente


class ClienteForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    tipo = SelectField(
        "Tipo",
        choices=[("PF", "Pessoa Física"), ("PJ", "Pessoa Jurídica")],
        default="PF",
        validators=[DataRequired()],
    )
    cpf_cnpj = StringField("CPF/CNPJ", validators=[Optional(), Length(max=20)])
    telefone = StringField("Telefone", validators=[Optional(), Length(max=20)])
    email = StringField("E-mail", validators=[Optional(), Email(), Length(max=120)])
    endereco = StringField("Endereço", validators=[Optional(), Length(max=255)])
    ativo = BooleanField("Ativo", default=True)
    submit = SubmitField("Salvar")

    def __init__(self, *args, cliente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._cliente = cliente

    def validate_cpf_cnpj(self, field):
        if not field.data:
            return
        query = Cliente.query.filter_by(cpf_cnpj=field.data.strip())
        if self._cliente:
            query = query.filter(Cliente.id != self._cliente.id)
        if query.first():
            raise ValidationError("Já existe um cliente cadastrado com este CPF/CNPJ.")
