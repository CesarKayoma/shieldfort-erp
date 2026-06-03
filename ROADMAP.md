# ROADMAP — Sistema de Gestão Comercial

> Documento gerado com base na análise do repositório atual.  
> Última atualização: Junho 2025

---

## Diagnóstico Atual

### Estado geral

O projeto está na fase de **esqueleto estrutural**. A fundação arquitetural foi corretamente estabelecida, mas nenhuma funcionalidade de negócio está implementada. O sistema inicializa sem erros, mas não é possível interagir com ele de forma útil.

### Pontos fortes

- Application Factory implementada corretamente em `app/__init__.py`
- Extensões centralizadas em `extensions.py`, evitando imports circulares
- Separação de ambientes (development/production) no `config.py`
- Todos os models definidos com relacionamentos e propriedades calculadas
- Blueprints registrados e prontos para receber lógica
- Suporte a variáveis de ambiente via `.env`

### Problemas identificados

- Todas as rotas retornam strings literais — nenhuma lógica implementada
- Camada de serviços (`services/`) completamente vazia
- Nenhum template HTML existe
- Sem autenticação — qualquer pessoa com a URL acessa tudo
- Sem validação de dados de entrada
- Sem tratamento de erros (sem página 404, sem rollback em exceções)
- `requirements.txt` sem versões fixadas — builds não são reproduzíveis
- `SECRET_KEY` tem valor padrão hardcoded — risco de segurança em produção
- `datetime.utcnow` está depreciado no Python 3.12+
- Nenhuma migration foi executada — o banco de dados não existe ainda
- Sem testes

### Riscos técnicos

| Risco | Impacto | Mitigação |
|---|---|---|
| `SECRET_KEY` padrão em produção | Alto — sessões comprometidas | Forçar variável de ambiente obrigatória |
| Sem autenticação | Alto — dados expostos | Implementar na Fase 4, antes de qualquer deploy |
| Versões não fixadas no `requirements.txt` | Médio — build quebra sem aviso | Fixar versões na Fase 1 |
| SQLite em produção | Médio — sem concorrência real | Migrar para PostgreSQL no deploy |
| `datetime.utcnow` depreciado | Baixo — warnings no Python 3.12+ | Corrigir durante implementação dos models |

---

## Fase 1 — Fundação

**Objetivo:** Garantir que o ambiente de desenvolvimento está correto, o banco de dados existe, e o projeto pode ser executado de forma reproduzível por qualquer desenvolvedor da equipe.

---

### Task 1.1 — Fixar versões das dependências

**Objetivo**  
Garantir que todos os desenvolvedores e o servidor de produção usem exatamente as mesmas versões de cada biblioteca.

**Por que é necessária**  
Sem versões fixadas, um `pip install` feito amanhã pode instalar versões diferentes das de hoje, quebrando o sistema silenciosamente.

**Passo a passo**

1. Ative o ambiente virtual: `source .venv/bin/activate`
2. Instale as dependências atuais: `pip install -r requirements.txt`
3. Gere o arquivo com versões exatas:
   ```bash
   pip freeze > requirements.txt
   ```
4. Revise o arquivo gerado e remova pacotes que não são dependências diretas do projeto (ex: `pkg-resources`). Mantenha apenas os que você instalou explicitamente e suas dependências transitivas.
5. Adicione ao `requirements.txt` os pacotes que serão necessários nas próximas fases:
   ```
   flask-login
   flask-wtf
   email-validator
   gunicorn
   psycopg2-binary
   ```

**Critério de conclusão**
- `requirements.txt` contém versões fixadas (ex: `Flask==3.0.3`)
- Qualquer desenvolvedor consegue rodar `pip install -r requirements.txt` e obter o mesmo ambiente

**Dependências**  
Nenhuma.

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 1.2 — Configurar variáveis de ambiente corretamente

**Objetivo**  
Separar configuração de código e garantir que a `SECRET_KEY` nunca tenha um valor padrão inseguro.

**Por que é necessária**  
A `SECRET_KEY` atual tem o valor `"dev-secret-key"` como fallback. Se alguém fizer o deploy sem configurar a variável de ambiente, as sessões de todos os usuários ficam vulneráveis.

**Passo a passo**

1. Abra `config.py` e altere a linha da `SECRET_KEY`:
   ```python
   # Antes
   SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

   # Depois
   SECRET_KEY = os.environ.get("SECRET_KEY")
   if not SECRET_KEY:
       raise ValueError("SECRET_KEY não definida. Configure a variável de ambiente.")
   ```

2. Adicione uma configuração de `homologacao` ao dicionário de configs:
   ```python
   class HomologacaoConfig(Config):
       DEBUG = False
       TESTING = True

   config = {
       "development": DevelopmentConfig,
       "homologacao": HomologacaoConfig,
       "production": ProductionConfig,
       "default": DevelopmentConfig,
   }
   ```

3. Atualize o `.env` com todos os valores necessários:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=gere-uma-chave-longa-e-aleatoria-aqui
   DATABASE_URL=sqlite:///db.sqlite3
   ```

4. Para gerar uma `SECRET_KEY` segura, rode no terminal:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Cole o resultado no `.env`.

5. Confirme que `.env` está no `.gitignore` (já está — só verificar).

**Critério de conclusão**
- A aplicação não inicializa se `SECRET_KEY` não estiver definida
- `.env` contém `FLASK_APP` e `SECRET_KEY` com valor real
- `.env` não está commitado no repositório

**Dependências**  
Nenhuma.

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 1.3 — Inicializar o banco de dados e executar migrations

**Objetivo**  
Criar o banco de dados SQLite e todas as tabelas definidas nos models.

**Por que é necessária**  
Sem este passo, o banco não existe. Qualquer rota que tente acessar dados vai lançar erro.

**Passo a passo**

1. Com o ambiente virtual ativo e o `.env` configurado, rode:
   ```bash
   flask db init
   ```
   Isso cria a pasta `migrations/` com os arquivos de controle do Alembic.

2. Gere a migration inicial:
   ```bash
   flask db migrate -m "initial schema"
   ```
   Isso analisa os models e gera um script de migration em `migrations/versions/`.

3. Revise o arquivo gerado em `migrations/versions/`. Confirme que todas as tabelas esperadas aparecem no `upgrade()`:
   - `clientes`
   - `categorias`
   - `orcamentos`
   - `itens_orcamento`
   - `vendas`
   - `instalacoes`
   - `servicos_recorrentes`
   - `pagamentos_mensais`
   - `clientes_starlink`
   - `comissoes_starlink`
   - `gastos_instalacao`

4. Aplique a migration:
   ```bash
   flask db upgrade
   ```

5. Confirme que o arquivo `db.sqlite3` foi criado na raiz do projeto.

6. Verifique as tabelas via terminal Python:
   ```bash
   flask shell
   ```
   ```python
   from app.extensions import db
   from sqlalchemy import inspect
   inspector = inspect(db.engine)
   print(inspector.get_table_names())
   ```

**Critério de conclusão**
- Arquivo `db.sqlite3` existe na raiz do projeto
- Comando `flask db upgrade` roda sem erros
- Todas as 11 tabelas aparecem no `inspect`

**Dependências**  
Task 1.2

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 1.4 — Corrigir depreciação de `datetime.utcnow`

**Objetivo**  
Substituir `datetime.utcnow` (depreciado no Python 3.12) por `datetime.now(timezone.utc)` em todos os models.

**Por que é necessária**  
O Python 3.12 emite `DeprecationWarning` para `datetime.utcnow`. Versões futuras vão remover o método. Melhor corrigir agora enquanto os arquivos são poucos.

**Passo a passo**

1. Nos arquivos `cliente.py`, `orcamento.py`, `venda.py`, `instalacao.py`, `servico_recorrente.py` e `starlink.py`, substitua:
   ```python
   # Antes
   from datetime import datetime
   criado_em = db.Column(db.DateTime, default=datetime.utcnow)

   # Depois
   from datetime import datetime, timezone
   criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
   ```

2. Faça o mesmo para `atualizado_em` em `orcamento.py`:
   ```python
   atualizado_em = db.Column(
       db.DateTime,
       default=lambda: datetime.now(timezone.utc),
       onupdate=lambda: datetime.now(timezone.utc)
   )
   ```

3. Rode `python run.py` e confirme que não há warnings no terminal.

**Critério de conclusão**
- Nenhum `DeprecationWarning` sobre `utcnow` ao iniciar a aplicação
- Todos os models importam `timezone` de `datetime`

**Dependências**  
Task 1.3

**Prioridade:** Média  
**Complexidade:** Baixa

---

## Fase 2 — Backend Core

**Objetivo:** Implementar a camada de serviços e todas as rotas com lógica real, validação de dados e tratamento de erros.

---

### Task 2.1 — Implementar tratamento global de erros

**Objetivo**  
Registrar handlers para os erros HTTP mais comuns e garantir que exceções não retornem stack traces para o usuário.

**Por que é necessária**  
Sem isso, um erro 404 retorna a página padrão do Flask (que vaza informações técnicas) e exceções não tratadas retornam stack traces que expõem detalhes da aplicação.

**Passo a passo**

1. Crie o arquivo `app/errors.py`:
   ```python
   from flask import render_template

   def register_error_handlers(app):
       @app.errorhandler(404)
       def not_found(e):
           return render_template("errors/404.html"), 404

       @app.errorhandler(500)
       def internal_error(e):
           return render_template("errors/500.html"), 500

       @app.errorhandler(403)
       def forbidden(e):
           return render_template("errors/403.html"), 403
   ```

2. Registre os handlers no `create_app` em `app/__init__.py`:
   ```python
   from app.errors import register_error_handlers

   def create_app(config_name="default"):
       # ... código existente ...
       register_error_handlers(app)
       return app
   ```

3. Crie os templates `app/templates/errors/404.html`, `403.html` e `500.html` (templates simples por enquanto — serão estilizados na Fase 3).

**Critério de conclusão**
- Acessar uma URL inexistente retorna a página `404.html` customizada
- Erros internos retornam `500.html` em vez de stack trace

**Dependências**  
Task 1.3

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 2.2 — Implementar camada de serviços — Clientes

**Objetivo**  
Criar `app/services/cliente_service.py` com toda a lógica de negócio para clientes, mantendo as rotas finas.

**Por que é necessária**  
Colocar lógica diretamente nas rotas torna o código difícil de testar e de reutilizar. A camada de serviço isola a lógica de negócio da camada HTTP.

**Passo a passo**

1. Crie `app/services/cliente_service.py`:
   ```python
   from app.extensions import db
   from app.models.cliente import Cliente

   def listar_clientes(busca=None):
       query = Cliente.query.order_by(Cliente.nome)
       if busca:
           query = query.filter(Cliente.nome.ilike(f"%{busca}%"))
       return query.all()

   def buscar_por_id(cliente_id):
       return Cliente.query.get_or_404(cliente_id)

   def criar_cliente(dados):
       cliente = Cliente(**dados)
       db.session.add(cliente)
       db.session.commit()
       return cliente

   def atualizar_cliente(cliente_id, dados):
       cliente = buscar_por_id(cliente_id)
       for campo, valor in dados.items():
           setattr(cliente, campo, valor)
       db.session.commit()
       return cliente

   def deletar_cliente(cliente_id):
       cliente = buscar_por_id(cliente_id)
       db.session.delete(cliente)
       db.session.commit()
   ```

2. Repita o mesmo padrão para os demais módulos nas tasks seguintes.

**Critério de conclusão**
- `cliente_service.py` existe com as 5 funções acima
- Nenhuma lógica de banco de dados está nas rotas

**Dependências**  
Task 1.3

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 2.3 — Implementar rotas de Clientes (CRUD completo)

**Objetivo**  
Substituir o stub `"clientes ok"` por rotas reais com listagem, criação, edição e exclusão.

**Por que é necessária**  
Clientes é a entidade central do sistema — orçamentos, vendas, instalações e mensalidades dependem de um cliente existir.

**Passo a passo**

1. Atualize `app/routes/clientes.py`:
   ```python
   from flask import Blueprint, render_template, request, redirect, url_for, flash
   from app.services import cliente_service

   bp = Blueprint("clientes", __name__)

   @bp.route("/")
   def index():
       busca = request.args.get("q", "")
       clientes = cliente_service.listar_clientes(busca=busca)
       return render_template("clientes/index.html", clientes=clientes, busca=busca)

   @bp.route("/novo", methods=["GET", "POST"])
   def novo():
       if request.method == "POST":
           dados = {
               "nome": request.form["nome"],
               "tipo": request.form["tipo"],
               "cpf_cnpj": request.form.get("cpf_cnpj"),
               "telefone": request.form.get("telefone"),
               "email": request.form.get("email"),
               "endereco": request.form.get("endereco"),
           }
           cliente_service.criar_cliente(dados)
           flash("Cliente cadastrado com sucesso.", "success")
           return redirect(url_for("clientes.index"))
       return render_template("clientes/form.html", cliente=None)

   @bp.route("/<int:cliente_id>/editar", methods=["GET", "POST"])
   def editar(cliente_id):
       cliente = cliente_service.buscar_por_id(cliente_id)
       if request.method == "POST":
           dados = {
               "nome": request.form["nome"],
               "tipo": request.form["tipo"],
               "cpf_cnpj": request.form.get("cpf_cnpj"),
               "telefone": request.form.get("telefone"),
               "email": request.form.get("email"),
               "endereco": request.form.get("endereco"),
           }
           cliente_service.atualizar_cliente(cliente_id, dados)
           flash("Cliente atualizado.", "success")
           return redirect(url_for("clientes.index"))
       return render_template("clientes/form.html", cliente=cliente)

   @bp.route("/<int:cliente_id>/deletar", methods=["POST"])
   def deletar(cliente_id):
       cliente_service.deletar_cliente(cliente_id)
       flash("Cliente removido.", "info")
       return redirect(url_for("clientes.index"))
   ```

2. Crie os templates `app/templates/clientes/index.html` e `app/templates/clientes/form.html` (detalhados na Fase 3).

**Critério de conclusão**
- `/clientes/` lista todos os clientes
- `/clientes/novo` cria um cliente via formulário
- `/clientes/<id>/editar` atualiza um cliente
- `/clientes/<id>/deletar` remove um cliente
- Flash messages aparecem após cada ação

**Dependências**  
Task 2.2

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 2.4 — Implementar serviços e rotas de Categorias

**Objetivo**  
CRUD completo de categorias (câmeras, Starlink, cerca elétrica, outros — criáveis pelo usuário).

**Por que é necessária**  
Categorias são necessárias antes de criar orçamentos, pois cada item de orçamento pode ter uma categoria.

**Passo a passo**

1. Crie `app/services/categoria_service.py` com funções `listar`, `criar`, `atualizar`, `deletar`.
2. Atualize `app/routes/categorias.py` — se o blueprint não existir ainda, crie e registre em `app/__init__.py`.
3. Crie os templates correspondentes.

> Siga o mesmo padrão da Task 2.3.

**Critério de conclusão**
- CRUD de categorias funcional via browser
- Categorias aparecem como opção ao criar itens de orçamento

**Dependências**  
Task 2.3

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 2.5 — Implementar serviços e rotas de Orçamentos

**Objetivo**  
CRUD de orçamentos com múltiplos itens, cálculo de total e fluxo de status.

**Por que é necessária**  
Orçamentos são o coração do sistema. A criação de vendas depende de um orçamento aprovado.

**Passo a passo**

1. Crie `app/services/orcamento_service.py` com funções:
   - `listar_orcamentos(cliente_id=None, status=None)`
   - `buscar_por_id(orcamento_id)`
   - `criar_orcamento(cliente_id, itens)` — cria o orçamento e seus itens em uma transação
   - `atualizar_status(orcamento_id, novo_status)` — valida transições permitidas
   - `aprovar_e_criar_venda(orcamento_id, forma_pagamento)` — transação atômica: aprova orçamento e cria venda

2. Implemente a rota `POST /orcamentos/<id>/aprovar` que:
   - Muda status do orçamento para `"aprovado"`
   - Cria o registro de `Venda` com `valor_total = orcamento.total`
   - Faz tudo em uma única transação (`db.session.commit()` uma vez só)

3. Formulário de orçamento requer JavaScript para adicionar/remover itens dinamicamente (detalhado na Fase 3).

4. Proteja transições de status — um orçamento `"aprovado"` não pode voltar para `"rascunho"`:
   ```python
   TRANSICOES_VALIDAS = {
       "rascunho": ["enviado", "recusado"],
       "enviado": ["aprovado", "recusado"],
       "aprovado": [],
       "recusado": [],
   }
   ```

**Critério de conclusão**
- Orçamento criado com 1 ou mais itens persiste no banco
- Status muda corretamente seguindo as transições permitidas
- Aprovar um orçamento cria automaticamente uma Venda
- Tentar transição inválida retorna erro com mensagem clara

**Dependências**  
Task 2.4

**Prioridade:** Alta  
**Complexidade:** Média

---

### Task 2.6 — Implementar serviços e rotas dos demais módulos

**Objetivo**  
Implementar CRUD funcional para: Vendas, Instalações, Serviços Recorrentes + Pagamentos Mensais, Clientes Starlink + Comissões, Gastos de Instalação.

**Por que é necessária**  
Completar a cobertura funcional do MVP.

**Passo a passo**

Para cada módulo, siga o padrão estabelecido nas tasks anteriores:

1. Crie o `_service.py` correspondente em `app/services/`
2. Atualize o blueprint em `app/routes/`
3. Crie os templates (Fase 3)

**Particularidades por módulo:**

- **Vendas:** Sem criação manual — são geradas pelo `orcamento_service`. Rotas de listagem, detalhe e atualização de status de pagamento.
- **Instalações:** Vinculadas a uma venda. Campo `tipo` define se é instalação ou manutenção. Campo `gratuita` indica manutenção inclusa em contrato.
- **Serviços Recorrentes:** Ao criar um `ServicoRecorrente`, gerar automaticamente os `PagamentoMensal` para os próximos 12 meses.
- **Pagamentos Mensais:** Rota `POST /recorrentes/<id>/pagar/<mes>` para marcar um mês como pago.
- **Gastos:** Vinculados a uma venda. Soma dos gastos pode ser comparada ao `valor_total` da venda para mostrar margem.

**Critério de conclusão**
- Todos os módulos têm listagem e criação funcionais
- Nenhuma rota retorna string literal

**Dependências**  
Task 2.5

**Prioridade:** Média  
**Complexidade:** Média

---

### Task 2.7 — Implementar Dashboard

**Objetivo**  
Rota `/` que retorna um template com as métricas definidas no planejamento.

**Por que é necessária**  
É a primeira tela que o usuário vê. Deve dar uma visão imediata do estado do negócio.

**Passo a passo**

1. Crie `app/services/dashboard_service.py`:
   ```python
   from app.models.venda import Venda
   from app.models.servico_recorrente import PagamentoMensal
   from datetime import datetime, timezone
   from sqlalchemy import func

   def obter_metricas():
       hoje = datetime.now(timezone.utc)
       mes_atual = hoje.strftime("%Y-%m")

       total_vendas_mes = (
           Venda.query
           .filter(func.strftime("%Y-%m", Venda.data_venda) == mes_atual)
           .with_entities(func.sum(Venda.valor_total))
           .scalar() or 0
       )

       pagamentos_pendentes = (
           PagamentoMensal.query
           .filter_by(status="pendente")
           .count()
       )

       return {
           "total_vendas_mes": total_vendas_mes,
           "pagamentos_pendentes": pagamentos_pendentes,
           # adicionar demais métricas
       }
   ```

2. Atualize `app/routes/dashboard.py` para usar o service e renderizar o template.

**Critério de conclusão**
- `/` exibe dados reais do banco, não strings hardcoded
- Métricas são calculadas via queries, não em Python puro

**Dependências**  
Task 2.6

**Prioridade:** Média  
**Complexidade:** Média

---

### Task 2.8 — Implementar validação de dados

**Objetivo**  
Garantir que dados inválidos não sejam persistidos no banco e que o usuário receba mensagens de erro claras.

**Por que é necessária**  
Sem validação, campos obrigatórios podem ser salvos vazios, CPFs inválidos podem ser inseridos, e valores negativos podem aparecer em orçamentos.

**Passo a passo**

1. Instale `flask-wtf` e `email-validator` (já devem estar no `requirements.txt` após a Task 1.1).

2. Crie `app/forms/cliente_form.py`:
   ```python
   from flask_wtf import FlaskForm
   from wtforms import StringField, SelectField
   from wtforms.validators import DataRequired, Optional, Email, Length

   class ClienteForm(FlaskForm):
       nome = StringField("Nome", validators=[DataRequired(), Length(min=2, max=120)])
       tipo = SelectField("Tipo", choices=[("PF", "Pessoa Física"), ("PJ", "Pessoa Jurídica")])
       cpf_cnpj = StringField("CPF/CNPJ", validators=[Optional(), Length(max=20)])
       telefone = StringField("Telefone", validators=[Optional(), Length(max=20)])
       email = StringField("E-mail", validators=[Optional(), Email()])
       endereco = StringField("Endereço", validators=[Optional(), Length(max=255)])
   ```

3. Atualize as rotas para usar os forms:
   ```python
   from app.forms.cliente_form import ClienteForm

   @bp.route("/novo", methods=["GET", "POST"])
   def novo():
       form = ClienteForm()
       if form.validate_on_submit():
           cliente_service.criar_cliente(form.data)
           flash("Cliente cadastrado.", "success")
           return redirect(url_for("clientes.index"))
       return render_template("clientes/form.html", form=form)
   ```

4. Repita para todos os módulos.

5. Configure o CSRF no `create_app`:
   ```python
   from flask_wtf.csrf import CSRFProtect
   csrf = CSRFProtect()
   csrf.init_app(app)
   ```

**Critério de conclusão**
- Formulários com campos obrigatórios vazios mostram erro sem salvar
- Token CSRF está presente em todos os formulários POST
- E-mails inválidos são rejeitados com mensagem clara

**Dependências**  
Task 2.3

**Prioridade:** Alta  
**Complexidade:** Média

---

## Fase 3 — Frontend

**Objetivo:** Criar todos os templates HTML com layout consistente, navegação funcional e formulários usáveis.

---

### Task 3.1 — Criar template base e layout principal

**Objetivo**  
Criar `app/templates/base.html` com sidebar de navegação, área de conteúdo e suporte a flash messages.

**Por que é necessária**  
Todos os outros templates herdam do base. Sem ele, nenhuma página tem navegação ou estilo consistente.

**Passo a passo**

1. Escolha um CSS framework leve. Recomendação: **Bootstrap 5** via CDN (sem build step, fácil de usar com Jinja2).

2. Crie `app/templates/base.html` com:
   - `<head>` com meta viewport, Bootstrap CSS via CDN
   - Sidebar com links para todos os módulos
   - Área `{% block content %}` para o conteúdo de cada página
   - Área de flash messages logo acima do conteúdo
   - Bootstrap JS via CDN no final do `<body>`

3. Estrutura básica da sidebar:
   ```
   Dashboard
   ─────────
   Clientes
   Orçamentos
   Vendas
   Instalações
   ─────────
   Recorrentes
   Starlink
   Gastos
   ─────────
   Categorias
   ```

4. Flash messages devem usar as classes Bootstrap correspondentes:
   - `"success"` → `alert-success`
   - `"info"` → `alert-info`
   - `"error"` → `alert-danger`

**Critério de conclusão**
- Todas as páginas exibem a sidebar
- Flash messages aparecem e somem automaticamente
- Layout é responsivo (funciona no celular)

**Dependências**  
Task 2.1

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 3.2 — Criar templates de Clientes

**Objetivo**  
Páginas de listagem e formulário para o módulo de clientes.

**Por que é necessária**  
Sem templates, as rotas existem mas não renderizam nada utilizável.

**Passo a passo**

1. Crie `app/templates/clientes/index.html`:
   - Tabela com colunas: Nome, Tipo, Telefone, E-mail, Mensalidade, Ações
   - Campo de busca no topo (`?q=`)
   - Botão "Novo Cliente"
   - Links de Editar e Deletar por linha

2. Crie `app/templates/clientes/form.html`:
   - Formulário com todos os campos do `ClienteForm`
   - Exibição de erros por campo
   - Botão de salvar e link de cancelar

3. Crie `app/templates/clientes/detail.html`:
   - Dados do cliente
   - Histórico de orçamentos
   - Histórico de instalações
   - Serviços recorrentes ativos

**Critério de conclusão**
- É possível listar, criar, editar e deletar clientes via browser
- Erros de validação aparecem nos campos correspondentes

**Dependências**  
Task 3.1 e Task 2.3

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 3.3 — Criar templates de Orçamentos

**Objetivo**  
Formulário de orçamento com adição dinâmica de itens via JavaScript.

**Por que é necessária**  
Orçamentos têm múltiplos itens — o formulário precisa de JS para adicionar/remover linhas dinamicamente sem recarregar a página.

**Passo a passo**

1. Crie `app/templates/orcamentos/form.html` com:
   - Campo de seleção de cliente
   - Tabela de itens com colunas: Descrição, Categoria, Quantidade, Preço Unitário, Subtotal, Remover
   - Botão "Adicionar Item" que clona uma linha via JavaScript
   - Total calculado em tempo real via JS
   - O formulário envia os itens como campos repetidos (ex: `item_descricao[]`, `item_quantidade[]`)

2. Script JS para cálculo em tempo real:
   ```javascript
   function calcularTotal() {
     let total = 0;
     document.querySelectorAll(".linha-item").forEach(linha => {
       const qtd = parseFloat(linha.querySelector(".qtd").value) || 0;
       const preco = parseFloat(linha.querySelector(".preco").value) || 0;
       const subtotal = qtd * preco;
       linha.querySelector(".subtotal").textContent = subtotal.toFixed(2);
       total += subtotal;
     });
     document.getElementById("total-geral").textContent = total.toFixed(2);
   }
   ```

3. Crie `app/templates/orcamentos/index.html` com filtro por status.

4. Crie `app/templates/orcamentos/detail.html` com:
   - Dados do orçamento e lista de itens
   - Botões de ação por status (ex: "Enviar", "Aprovar", "Recusar")

**Critério de conclusão**
- É possível criar orçamento com múltiplos itens
- Total atualiza em tempo real ao digitar quantidades e preços
- Botão "Aprovar" cria a venda e redireciona para ela

**Dependências**  
Task 3.2 e Task 2.5

**Prioridade:** Alta  
**Complexidade:** Média

---

### Task 3.4 — Criar templates dos demais módulos

**Objetivo**  
Templates de listagem e formulário para: Vendas, Instalações, Serviços Recorrentes, Starlink, Gastos e Dashboard.

**Passo a passo**

Siga o padrão dos módulos anteriores. Particularidades:

- **Vendas:** Sem formulário de criação. Exibir botão "Marcar como Pago".
- **Instalações:** Exibir badge colorido por tipo (instalação vs manutenção).
- **Recorrentes:** Tabela de pagamentos mensais com checkbox por mês.
- **Dashboard:** Cards com métricas, gráfico simples de vendas por categoria (pode usar Chart.js via CDN).

**Critério de conclusão**
- Todos os módulos têm listagem funcional
- Nenhum template retorna erro 500

**Dependências**  
Task 3.3

**Prioridade:** Média  
**Complexidade:** Média

---

## Fase 4 — Autenticação

**Objetivo:** Proteger todas as rotas com login obrigatório.

---

### Task 4.1 — Implementar autenticação com Flask-Login

**Objetivo**  
Criar sistema de login/logout e proteger todas as rotas existentes.

**Por que é necessária**  
Sem autenticação, qualquer pessoa com a URL do sistema acessa todos os dados da empresa.

**Passo a passo**

1. Adicione `flask-login` ao `requirements.txt` (já deve estar após Task 1.1).

2. Crie o model `app/models/usuario.py`:
   ```python
   from app.extensions import db
   from flask_login import UserMixin
   from werkzeug.security import generate_password_hash, check_password_hash

   class Usuario(db.Model):
       __tablename__ = "usuarios"
       id = db.Column(db.Integer, primary_key=True)
       nome = db.Column(db.String(120), nullable=False)
       email = db.Column(db.String(120), unique=True, nullable=False)
       senha_hash = db.Column(db.String(256), nullable=False)
       ativo = db.Column(db.Boolean, default=True)

       def set_senha(self, senha):
           self.senha_hash = generate_password_hash(senha)

       def verificar_senha(self, senha):
           return check_password_hash(self.senha_hash, senha)
   ```

3. Adicione `LoginManager` ao `app/extensions.py`:
   ```python
   from flask_login import LoginManager
   login_manager = LoginManager()
   login_manager.login_view = "auth.login"
   login_manager.login_message = "Faça login para continuar."
   ```

4. Registre no `create_app`:
   ```python
   from app.extensions import login_manager

   login_manager.init_app(app)

   @login_manager.user_loader
   def load_user(user_id):
       from app.models.usuario import Usuario
       return Usuario.query.get(int(user_id))
   ```

5. Crie `app/routes/auth.py` com rotas `GET/POST /login` e `GET /logout`.

6. Adicione `@login_required` a todos os blueprints existentes.

7. Crie uma migration para a tabela `usuarios` e aplique.

8. Crie um script de seed para criar o primeiro usuário:
   ```bash
   # scripts/criar_usuario.py
   flask shell
   ```
   ```python
   from app.models.usuario import Usuario
   from app.extensions import db
   u = Usuario(nome="Admin", email="admin@empresa.com")
   u.set_senha("troque-essa-senha")
   db.session.add(u)
   db.session.commit()
   ```

**Critério de conclusão**
- Acessar qualquer rota sem login redireciona para `/login`
- Login com credenciais corretas redireciona para o dashboard
- Login com credenciais erradas exibe mensagem de erro
- Logout encerra a sessão e redireciona para `/login`

**Dependências**  
Task 3.4

**Prioridade:** Alta  
**Complexidade:** Média

---

## Fase 5 — Segurança

**Objetivo:** Aplicar proteções básicas antes do deploy.

---

### Task 5.1 — Configurar headers de segurança

**Objetivo**  
Adicionar headers HTTP que protegem contra ataques comuns (XSS, clickjacking, MIME sniffing).

**Por que é necessária**  
Flask não adiciona esses headers por padrão. São configurações de uma linha que eliminam classes inteiras de vulnerabilidades.

**Passo a passo**

1. Instale `flask-talisman`:
   ```bash
   pip install flask-talisman
   ```

2. Configure no `create_app` (desabilitar HTTPS em dev):
   ```python
   from flask_talisman import Talisman

   if config_name == "production":
       Talisman(app, force_https=True)
   ```

**Critério de conclusão**
- Em produção, requisições HTTP são redirecionadas para HTTPS
- Headers `X-Frame-Options`, `X-Content-Type-Options` e `X-XSS-Protection` estão presentes nas respostas

**Dependências**  
Task 4.1

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 5.2 — Configurar logs da aplicação

**Objetivo**  
Registrar erros e ações importantes em arquivo de log, com nível de detalhe adequado por ambiente.

**Por que é necessária**  
Sem logs, quando algo der errado em produção, não haverá como investigar o que aconteceu.

**Passo a passo**

1. Atualize `app/__init__.py` para configurar logging:
   ```python
   import logging
   from logging.handlers import RotatingFileHandler
   import os

   def configure_logging(app):
       if not app.debug:
           if not os.path.exists("logs"):
               os.mkdir("logs")
           handler = RotatingFileHandler(
               "logs/app.log", maxBytes=10240, backupCount=10
           )
           handler.setFormatter(logging.Formatter(
               "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
           ))
           handler.setLevel(logging.INFO)
           app.logger.addHandler(handler)
           app.logger.setLevel(logging.INFO)
           app.logger.info("Aplicação iniciada")
   ```

2. Registre erros nos handlers de exceção:
   ```python
   @app.errorhandler(500)
   def internal_error(e):
       app.logger.error(f"Erro 500: {e}")
       return render_template("errors/500.html"), 500
   ```

3. Adicione `logs/` ao `.gitignore`.

**Critério de conclusão**
- Em produção, erros aparecem em `logs/app.log`
- Em desenvolvimento, logs aparecem no terminal
- Arquivo de log não é commitado no repositório

**Dependências**  
Task 2.1

**Prioridade:** Alta  
**Complexidade:** Baixa

---

## Fase 6 — Testes

**Objetivo:** Cobrir a lógica crítica com testes automatizados.

---

### Task 6.1 — Configurar ambiente de testes

**Objetivo**  
Instalar pytest e criar a configuração base para testes com banco de dados em memória.

**Por que é necessária**  
Testes automatizados evitam que mudanças quebrem funcionalidades existentes sem que ninguém perceba.

**Passo a passo**

1. Instale as dependências:
   ```bash
   pip install pytest pytest-flask
   ```
   Adicione ao `requirements.txt`.

2. Crie `tests/conftest.py`:
   ```python
   import pytest
   from app import create_app
   from app.extensions import db as _db

   @pytest.fixture(scope="session")
   def app():
       app = create_app("testing")
       with app.app_context():
           _db.create_all()
           yield app
           _db.drop_all()

   @pytest.fixture
   def client(app):
       return app.test_client()

   @pytest.fixture
   def db(app):
       yield _db
       _db.session.rollback()
   ```

3. Adicione a config `TestingConfig` ao `config.py`:
   ```python
   class TestingConfig(Config):
       TESTING = True
       SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
       WTF_CSRF_ENABLED = False
       SECRET_KEY = "test-secret"
   ```

**Critério de conclusão**
- `pytest` roda sem erros com zero testes
- Banco em memória é criado e destruído a cada sessão de testes

**Dependências**  
Task 1.3

**Prioridade:** Média  
**Complexidade:** Baixa

---

### Task 6.2 — Escrever testes dos serviços

**Objetivo**  
Cobrir a lógica de negócio crítica: criação de clientes, fluxo de orçamento → venda, e mensalidades.

**Por que é necessária**  
Os serviços contêm as regras de negócio mais importantes. São os primeiros a serem testados.

**Passo a passo**

1. Crie `tests/test_cliente_service.py`:
   ```python
   def test_criar_cliente(db):
       from app.services import cliente_service
       cliente = cliente_service.criar_cliente({"nome": "João", "tipo": "PF"})
       assert cliente.id is not None
       assert cliente.nome == "João"

   def test_buscar_cliente_inexistente(client):
       response = client.get("/clientes/9999/editar")
       assert response.status_code == 404
   ```

2. Crie `tests/test_orcamento_service.py` cobrindo:
   - Criação de orçamento com itens
   - Cálculo correto do total
   - Transição de status válida
   - Transição de status inválida (deve lançar exceção)
   - Aprovação cria venda com valor correto

**Critério de conclusão**
- `pytest` passa com todos os testes verdes
- Cobertura mínima de 70% nos arquivos `services/`

**Dependências**  
Task 6.1

**Prioridade:** Média  
**Complexidade:** Média

---

## Fase 7 — Deploy

**Objetivo:** Colocar o sistema em produção em um servidor acessível pela internet.

---

### Task 7.1 — Preparar a aplicação para produção

**Objetivo**  
Adicionar WSGI server, `Procfile` e garantir que a aplicação funciona fora do servidor de desenvolvimento do Flask.

**Por que é necessária**  
`flask run` não é adequado para produção — não suporta concorrência e expõe o debugger. Gunicorn é o servidor WSGI padrão para Flask em produção.

**Passo a passo**

1. Confirme que `gunicorn` está no `requirements.txt`.

2. Crie `Procfile` na raiz:
   ```
   web: gunicorn "app:create_app('production')" --workers 2 --bind 0.0.0.0:$PORT
   ```

3. Crie `runtime.txt` na raiz (para Railway/Render):
   ```
   python-3.12.3
   ```

4. Teste localmente:
   ```bash
   gunicorn "app:create_app('production')" --workers 2
   ```

**Critério de conclusão**
- Gunicorn inicia sem erros em modo production
- Aplicação responde em `http://localhost:8000`

**Dependências**  
Task 5.2

**Prioridade:** Alta  
**Complexidade:** Baixa

---

### Task 7.2 — Configurar banco de dados PostgreSQL em produção

**Objetivo**  
Substituir SQLite por PostgreSQL no ambiente de produção, usando Neon ou serviço similar.

**Por que é necessária**  
SQLite não suporta múltiplas conexões concorrentes. Em produção com Gunicorn rodando múltiplos workers, ocorrerão erros de lock no banco.

**Passo a passo**

1. Crie uma instância PostgreSQL no Neon (neon.tech) ou no próprio Railway.

2. Copie a connection string fornecida. Ela terá o formato:
   ```
   postgresql://usuario:senha@host/banco
   ```

3. No painel do Railway/Render, adicione a variável de ambiente:
   ```
   DATABASE_URL=postgresql://usuario:senha@host/banco
   ```

4. A aplicação já usa `DATABASE_URL` do ambiente — nenhuma mudança no código é necessária.

5. Após o primeiro deploy, rode as migrations em produção:
   ```bash
   flask db upgrade
   ```
   No Railway/Render, isso pode ser configurado como um comando de release.

6. Crie o primeiro usuário em produção via `flask shell` ou via script de seed.

**Critério de conclusão**
- Aplicação em produção usa PostgreSQL
- `flask db upgrade` roda sem erros no ambiente de produção
- Dados persistem entre restarts do servidor

**Dependências**  
Task 7.1

**Prioridade:** Alta  
**Complexidade:** Média

---

### Task 7.3 — Deploy no Railway ou Render

**Objetivo**  
Publicar a aplicação em um servidor acessível pela internet.

**Por que é necessária**  
O sistema precisa estar disponível para os dois sócios acessarem de qualquer lugar, não apenas na máquina do desenvolvedor.

**Passo a passo (Railway)**

1. Crie uma conta em [railway.app](https://railway.app)

2. No painel, clique em "New Project" → "Deploy from GitHub repo"

3. Selecione o repositório do projeto

4. Configure as variáveis de ambiente:
   ```
   SECRET_KEY=<valor gerado com secrets.token_hex(32)>
   DATABASE_URL=<connection string do PostgreSQL>
   FLASK_ENV=production
   ```

5. O Railway detecta o `Procfile` automaticamente e inicia o deploy

6. Após o deploy, acesse o terminal do projeto e rode:
   ```bash
   flask db upgrade
   python scripts/criar_usuario.py
   ```

7. Acesse a URL gerada pelo Railway e confirme que o login funciona

**Critério de conclusão**
- Aplicação acessível via URL pública
- Login funciona com o usuário criado
- Dados salvos persistem após restart

**Dependências**  
Task 7.2

**Prioridade:** Alta  
**Complexidade:** Baixa

---

## Fase 8 — Qualidade e Manutenção

**Objetivo:** Garantir que o projeto seja sustentável a longo prazo.

---

### Task 8.1 — Configurar linter e formatador de código

**Objetivo**  
Manter o código consistente e livre de erros óbvios automaticamente.

**Passo a passo**

1. Instale as ferramentas:
   ```bash
   pip install ruff
   ```

2. Crie `pyproject.toml` na raiz:
   ```toml
   [tool.ruff]
   line-length = 100
   target-version = "py312"
   ```

3. Adicione ao `requirements.txt`.

4. Rode antes de commitar:
   ```bash
   ruff check .
   ruff format .
   ```

**Critério de conclusão**
- `ruff check .` passa sem erros
- Todos os desenvolvedores usam a mesma configuração

**Dependências**  
Nenhuma.

**Prioridade:** Baixa  
**Complexidade:** Baixa

---

### Task 8.2 — Documentar processo de setup e deploy

**Objetivo**  
Criar um `README.md` que permita que qualquer desenvolvedor configure e rode o projeto do zero.

**Passo a passo**

1. Crie `README.md` na raiz com:
   - Descrição do projeto (1 parágrafo)
   - Pré-requisitos (Python 3.12+, pip)
   - Setup local passo a passo
   - Variáveis de ambiente necessárias
   - Como rodar os testes
   - Como fazer deploy
   - Como criar o primeiro usuário

**Critério de conclusão**
- Um desenvolvedor que nunca viu o projeto consegue rodar localmente seguindo o README
- Todas as variáveis de ambiente estão documentadas

**Dependências**  
Task 7.3

**Prioridade:** Média  
**Complexidade:** Baixa

---

### Task 8.3 — Configurar backup do banco de dados

**Objetivo**  
Garantir que os dados não sejam perdidos em caso de falha.

**Passo a passo**

1. Se usando Neon: backups automáticos já estão incluídos no plano gratuito. Verifique a configuração no painel.

2. Se usando Railway PostgreSQL: configure um cron job semanal que exporta o banco:
   ```bash
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   ```

3. Armazene os backups em local separado (Google Drive, S3, etc.).

**Critério de conclusão**
- Existe um processo documentado de backup
- Pelo menos um backup bem-sucedido foi testado e restaurado

**Dependências**  
Task 7.2

**Prioridade:** Alta  
**Complexidade:** Baixa

---

## Resumo das Fases

| Fase | Foco | Tasks | Estimativa |
|---|---|---|---|
| Fase 1 | Fundação | 4 tasks | 2–3 horas |
| Fase 2 | Backend Core | 8 tasks | 2–3 dias |
| Fase 3 | Frontend | 4 tasks | 2–3 dias |
| Fase 4 | Autenticação | 1 task | 4–6 horas |
| Fase 5 | Segurança | 2 tasks | 2–3 horas |
| Fase 6 | Testes | 2 tasks | 1–2 dias |
| Fase 7 | Deploy | 3 tasks | 4–6 horas |
| Fase 8 | Manutenção | 3 tasks | 2–3 horas |

**Total estimado:** 8–14 dias de trabalho efetivo para dois desenvolvedores.

---

## Ordem de execução recomendada

```
1.1 → 1.2 → 1.3 → 1.4
             ↓
           2.1 → 2.2 → 2.3 → 2.4 → 2.5 → 2.6 → 2.7 → 2.8
                                                        ↓
                                               3.1 → 3.2 → 3.3 → 3.4
                                                                   ↓
                                                                 4.1
                                                                   ↓
                                                          5.1 → 5.2
                                                                   ↓
                                                          6.1 → 6.2
                                                                   ↓
                                                       7.1 → 7.2 → 7.3
                                                                   ↓
                                                       8.1 → 8.2 → 8.3
```

> As Fases 1, 2 e 4 são **bloqueantes** — nada vai para produção sem elas.  
> As Fases 6 e 8 podem ser desenvolvidas em paralelo com as demais.
