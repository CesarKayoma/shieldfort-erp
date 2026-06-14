from app.extensions import db
from app.models import Servico
from app.models.pagamento import FormaPagamento
from app.models.servico import StatusServico
from app.services import pagamento_service

PER_PAGE = 10


def listar_servicos(status="", page=1, per_page=PER_PAGE):
    query = Servico.query
    if status:
        query = query.filter(Servico.status == StatusServico(status))
    return query.order_by(Servico.criado_em.desc()).paginate(page=page, per_page=per_page)


def contar_servicos():
    return Servico.query.count()


def obter_servico(id):
    return Servico.query.get_or_404(id)


def criar_servico(form):
    servico = Servico()
    _aplicar_form(servico, form)
    _aplicar_pagamento(servico, form)
    db.session.add(servico)
    db.session.commit()
    return servico


def atualizar_servico(servico, form):
    _aplicar_form(servico, form)
    _aplicar_pagamento(servico, form)
    db.session.commit()
    return servico


def excluir_servico(servico):
    db.session.delete(servico)
    db.session.commit()


def _aplicar_form(servico, form):
    servico.orcamento_id = form.orcamento_id.data
    servico.status = StatusServico(form.status.data)
    servico.data_execucao = form.data_execucao.data
    servico.observacoes = (form.observacoes.data or "").strip() or None
    servico.ativo = form.ativo.data


def _aplicar_pagamento(servico, form):
    pagamento_service.aplicar_pagamento(
        servico,
        valor_total=form.valor_servico.data,
        forma_pagamento=FormaPagamento(form.forma_pagamento.data),
        numero_parcelas=form.numero_parcelas.data,
        data_primeira_parcela=form.data_primeira_parcela.data,
    )
