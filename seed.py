"""Popula o banco com dados de exemplo para desenvolvimento.

Rode com:  python seed.py

Os dados são criados na ordem das dependencias de chave estrangeira:
unidades/categorias -> produtos -> clientes -> orcamentos -> itens.
"""
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models import (
    Cliente,
    Orcamento,
    ItemOrcamento,
    Produto,
    CategoriaProduto,
    UnidadeMedida,
    User
)
from app.models.orcamento import StatusOrcamento

app = create_app()

with app.app_context():
    # 1. Limpa dados antigos (ordem INVERSA das dependencias, para nao violar FK)
    User.query.delete()
    ItemOrcamento.query.delete()
    Orcamento.query.delete()
    Produto.query.delete()
    Cliente.query.delete()
    CategoriaProduto.query.delete()
    UnidadeMedida.query.delete()
    db.session.commit()

    # 2. Usuario admin para desenvolvimento
    admin = User(
        nome="Admin",
        email="admin@shieldfort.com",
        ativo=True,
    )
    admin.set_senha("admin123")
    db.session.add(admin)
    db.session.commit()

    # 2. Unidades de medida e categorias (sem dependencias)
    un = UnidadeMedida(sigla="UN", descricao="Unidade")
    hr = UnidadeMedida(sigla="HR", descricao="Hora")
    cat_pecas = CategoriaProduto(nome="Pecas")
    cat_servicos = CategoriaProduto(nome="Servicos")
    db.session.add_all([un, hr, cat_pecas, cat_servicos])
    db.session.commit()

    # 3. Produtos (dependem de categoria + unidade de medida)
    filtro = Produto(
        nome="Filtro de oleo",
        descricao="Filtro de oleo para trator",
        categoria_id=cat_pecas.id,
        unidade_medida_id=un.id,
        valor_padrao=Decimal("150.00"),
    )
    revisao = Produto(
        nome="Revisao de 250h",
        descricao="Mao de obra de revisao programada",
        categoria_id=cat_servicos.id,
        unidade_medida_id=hr.id,
        valor_padrao=Decimal("200.00"),
    )
    db.session.add_all([filtro, revisao])
    db.session.commit()

    # 4. Clientes (sem dependencias)
    cliente = Cliente(
        nome="Fazenda Boa Vista",
        tipo="PJ",
        cpf_cnpj="12345678000199",
        email="contato@boavista.com",
        telefone="99 99999-9999",
    )
    db.session.add(cliente)
    db.session.commit()

    # 5. Orcamento (depende de cliente)
    orcamento = Orcamento(
        cliente_id=cliente.id,
        status=StatusOrcamento.RASCUNHO,
    )
    db.session.add(orcamento)
    db.session.commit()

    # 6. Itens do orcamento (dependem de orcamento + categoria + produto)
    itens = [
        ItemOrcamento(
            orcamento_id=orcamento.id,
            categoria_id=cat_pecas.id,
            produto_id=filtro.id,
            descricao="Filtro de oleo",
            quantidade=Decimal("3.00"),
            preco_unitario=Decimal("150.00"),
        ),
        ItemOrcamento(
            orcamento_id=orcamento.id,
            categoria_id=cat_servicos.id,
            produto_id=revisao.id,
            descricao="Revisao de 250h",
            quantidade=Decimal("2.00"),
            preco_unitario=Decimal("200.00"),
        ),
    ]
    db.session.add_all(itens)
    db.session.commit()

    # 7. Resumo do que foi criado
    print("Seed concluido:")
    print(f"  {UnidadeMedida.query.count()} unidades de medida")
    print(f"  {CategoriaProduto.query.count()} categorias")
    print(f"  {Produto.query.count()} produtos")
    print(f"  {Cliente.query.count()} clientes")
    print(f"  {Orcamento.query.count()} orcamentos")
    print(f"  {ItemOrcamento.query.count()} itens de orcamento")
    print(f"  {User.query.count()} usuarios")
    print(f"  Total do orcamento #{orcamento.id}: R$ {orcamento.total}")
