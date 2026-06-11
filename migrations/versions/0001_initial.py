"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-11

Tabelas criadas:
    - unidades_medidas
    - categorias_produtos
    - produtos
    - clientes
    - orcamentos
    - itens_orcamento
"""

from alembic import op
import sqlalchemy as sa


# ── metadados do Alembic ────────────────────────────────────────────────────
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── 1. unidades_medidas ─────────────────────────────────────────────────
    # Sem dependências externas — criada primeiro.
    op.create_table(
        "unidades_medidas",
        sa.Column("id",          sa.Integer(),     nullable=False),
        sa.Column("sigla",       sa.String(120),   nullable=False),
        sa.Column("descricao",   sa.String(255),   nullable=False),
        sa.Column("criado_em",   sa.DateTime(),    nullable=False),
        sa.Column("atualizado_em", sa.DateTime(),  nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_unidades_medidas"),
    )

    # ── 2. categorias_produtos ──────────────────────────────────────────────
    # Sem dependências externas — criada antes de produtos e itens_orcamento.
    op.create_table(
        "categorias_produtos",
        sa.Column("id",          sa.Integer(),     nullable=False),
        sa.Column("nome",        sa.String(120),   nullable=False),
        sa.Column("criado_em",   sa.DateTime(),    nullable=False),
        sa.Column("atualizado_em", sa.DateTime(),  nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_categorias_produtos"),
    )

    # ── 3. produtos ─────────────────────────────────────────────────────────
    # Depende de: categorias_produtos, unidades_medidas
    op.create_table(
        "produtos",
        sa.Column("id",                 sa.Integer(),        nullable=False),
        sa.Column("nome",               sa.String(120),      nullable=False),
        sa.Column("descricao",          sa.String(255),      nullable=False),
        sa.Column("categoria_id",       sa.Integer(),        nullable=False),
        sa.Column("unidade_medida_id",  sa.Integer(),        nullable=False),
        sa.Column("ativo",              sa.Boolean(),        nullable=False, server_default=sa.true()),
        sa.Column("valor_padrao",       sa.Numeric(10, 2),   nullable=True),
        sa.Column("criado_em",          sa.DateTime(),       nullable=False),
        sa.Column("atualizado_em",      sa.DateTime(),       nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_produtos"),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categorias_produtos.id"],
            name="fk_produtos_categoria_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["unidade_medida_id"],
            ["unidades_medidas.id"],
            name="fk_produtos_unidade_medida_id",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_produtos_categoria_id",      "produtos", ["categoria_id"])
    op.create_index("ix_produtos_unidade_medida_id", "produtos", ["unidade_medida_id"])
    op.create_index("ix_produtos_ativo",             "produtos", ["ativo"])

    # ── 4. clientes ─────────────────────────────────────────────────────────
    # Sem dependências externas.
    op.create_table(
        "clientes",
        sa.Column("id",          sa.Integer(),     nullable=False),
        sa.Column("nome",        sa.String(120),   nullable=False),
        sa.Column("tipo",        sa.String(2),     nullable=False, server_default="PF"),
        sa.Column("cpf_cnpj",    sa.String(20),    nullable=True),
        sa.Column("telefone",    sa.String(20),    nullable=True),
        sa.Column("email",       sa.String(120),   nullable=True),
        sa.Column("endereco",    sa.String(255),   nullable=True),
        sa.Column("ativo",       sa.Boolean(),     nullable=False, server_default=sa.true()),
        sa.Column("criado_em",   sa.DateTime(),    nullable=False),
        sa.Column("atualizado_em", sa.DateTime(),  nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_clientes"),
        sa.UniqueConstraint("cpf_cnpj", name="uq_clientes_cpf_cnpj"),
        sa.CheckConstraint("tipo IN ('PF', 'PJ')", name="ck_clientes_tipo"),
    )
    op.create_index("ix_clientes_ativo", "clientes", ["ativo"])

    # ── 5. orcamentos ───────────────────────────────────────────────────────
    # Depende de: clientes
    op.create_table(
        "orcamentos",
        sa.Column("id",          sa.Integer(),     nullable=False),
        sa.Column("cliente_id",  sa.Integer(),     nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "rascunho", "enviado", "aprovado", "recusado",
                name="status_orcamento",
            ),
            nullable=False,
            server_default="rascunho",
        ),
        sa.Column("ativo",       sa.Boolean(),     nullable=False, server_default=sa.true()),
        sa.Column("criado_em",   sa.DateTime(),    nullable=False),
        sa.Column("atualizado_em", sa.DateTime(),  nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_orcamentos"),
        sa.ForeignKeyConstraint(
            ["cliente_id"],
            ["clientes.id"],
            name="fk_orcamentos_cliente_id",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_orcamentos_cliente_id", "orcamentos", ["cliente_id"])
    op.create_index("ix_orcamentos_status",     "orcamentos", ["status"])

    # ── 6. itens_orcamento ──────────────────────────────────────────────────
    # Depende de: orcamentos, categorias_produtos, produtos
    op.create_table(
        "itens_orcamento",
        sa.Column("id",              sa.Integer(),       nullable=False),
        sa.Column("orcamento_id",    sa.Integer(),       nullable=False),
        sa.Column("categoria_id",    sa.Integer(),       nullable=False),
        sa.Column("produto_id",      sa.Integer(),       nullable=False),
        sa.Column("descricao",       sa.String(255),     nullable=False),
        sa.Column("quantidade",      sa.Numeric(10, 2),  nullable=False, server_default="1.00"),
        sa.Column("preco_unitario",  sa.Numeric(10, 2),  nullable=False, server_default="0.00"),
        sa.Column("criado_em",       sa.DateTime(),      nullable=False),
        sa.Column("atualizado_em",   sa.DateTime(),      nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_itens_orcamento"),
        sa.ForeignKeyConstraint(
            ["orcamento_id"],
            ["orcamentos.id"],
            name="fk_itens_orcamento_orcamento_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["categoria_id"],
            ["categorias_produtos.id"],
            name="fk_itens_orcamento_categoria_id",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["produto_id"],
            ["produtos.id"],
            name="fk_itens_orcamento_produto_id",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("quantidade > 0",      name="ck_itens_orcamento_quantidade_positiva"),
        sa.CheckConstraint("preco_unitario >= 0", name="ck_itens_orcamento_preco_nao_negativo"),
    )
    op.create_index("ix_itens_orcamento_orcamento_id", "itens_orcamento", ["orcamento_id"])
    op.create_index("ix_itens_orcamento_categoria_id", "itens_orcamento", ["categoria_id"])
    op.create_index("ix_itens_orcamento_produto_id",   "itens_orcamento", ["produto_id"])


def downgrade() -> None:
    # ordem inversa da criação — respeita as dependências de FK
    op.drop_table("itens_orcamento")

    op.drop_index("ix_orcamentos_status",     table_name="orcamentos")
    op.drop_index("ix_orcamentos_cliente_id", table_name="orcamentos")
    op.drop_table("orcamentos")
    op.execute("DROP TYPE IF EXISTS status_orcamento")

    op.drop_index("ix_clientes_ativo", table_name="clientes")
    op.drop_table("clientes")

    op.drop_index("ix_produtos_ativo",             table_name="produtos")
    op.drop_index("ix_produtos_unidade_medida_id", table_name="produtos")
    op.drop_index("ix_produtos_categoria_id",      table_name="produtos")
    op.drop_table("produtos")

    op.drop_table("categorias_produtos")
    op.drop_table("unidades_medidas")
