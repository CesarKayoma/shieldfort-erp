# Shieldfort ERP

Sistema de gestão comercial desenvolvido para a Shieldfort, empresa especializada em instalação de equipamentos de segurança (câmeras, cercas elétricas) e internet via Starlink. O sistema centraliza o controle de clientes, orçamentos, serviços prestados, pagamentos e gastos da operação, substituindo o controle manual por planilhas.

Este projeto foi desenvolvido no contexto de um projeto de extensão universitária, com o objetivo de aplicar conhecimentos de engenharia de software na solução de um problema real de uma pequena empresa.

## Funcionalidades

- **Clientes**: cadastro, busca e edição de clientes (pessoa física e jurídica).
- **Produtos**: catálogo de produtos/serviços, organizados por categoria e unidade de medida, com preço padrão.
- **Orçamentos**: criação de orçamentos com múltiplos itens, cálculo automático do total e fluxo de status (rascunho → enviado → aprovado/recusado).
- **Serviços**: geração de um serviço a partir de um orçamento aprovado, com acompanhamento de execução (agendado, em andamento, concluído, cancelado).
- **Pagamentos**: controle de recebimentos vinculados aos serviços, com suporte a parcelamento (cartão de crédito em N vezes; demais formas em parcela única).
- **Gastos**: registro de despesas da operação, também com parcelamento e controle de vencimento/pagamento.
- **Dashboard**: visão geral com indicadores do mês (faturamento, clientes ativos, instalações), resumo financeiro (a receber, a pagar, parcelas atrasadas) e agenda dos próximos serviços.
- **Autenticação**: acesso restrito por login (Flask-Login).

## Tecnologias e arquitetura

- **Python 3.12 + Flask**, organizado no padrão *Application Factory* (`app/__init__.py`), com a lógica separada em camadas:
  - `app/models` — entidades e regras de dados (SQLAlchemy);
  - `app/services` — regras de negócio (criação, cálculo de parcelas, transições de status etc.), mantendo as rotas finas;
  - `app/routes` — blueprints com as rotas HTTP;
  - `app/forms` — validação de formulários (Flask-WTF), com proteção CSRF;
  - `app/templates` — interface (HTML + Tailwind CSS).
- **Banco de dados**: PostgreSQL em produção (hospedado no Neon) e SQLite como alternativa local, gerenciado via **Flask-Migrate / Alembic**.
- **Autenticação**: Flask-Login com senhas armazenadas com hash (Werkzeug).
- **Servidor de produção**: Gunicorn (ver `Procfile`).

## Como executar localmente

### Pré-requisitos

- Python 3.12+
- pip

### Passo a passo

1. Clone o repositório e acesse a pasta do projeto.

2. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo:

   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=<gere uma chave com o comando abaixo>
   DATABASE_URL=<string de conexão do banco — opcional em dev, usa SQLite local se omitida>
   ```

   Para gerar uma `SECRET_KEY` segura:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Aplique as migrations para criar as tabelas no banco:

   ```bash
   flask db upgrade
   ```

6. (Opcional) Popule o banco com dados de exemplo e um usuário administrador:

   ```bash
   python seed.py
   ```

   Isso cria o usuário `admin@shieldfort.com` com senha `admin123`. **Troque essa senha antes de usar fora de ambiente de desenvolvimento.**

7. Inicie a aplicação:

   ```bash
   python run.py
   ```

8. Acesse [http://localhost:5000](http://localhost:5000) e faça login.

## Variáveis de ambiente

| Variável | Descrição | Obrigatória |
|---|---|---|
| `FLASK_APP` | Ponto de entrada da aplicação (`run.py`) | Sim |
| `FLASK_ENV` | `development` ou `production` — define o modo de execução (debug, etc.) | Sim |
| `SECRET_KEY` | Chave usada para sessões e proteção CSRF. A aplicação não inicia sem ela | Sim |
| `DATABASE_URL` | String de conexão do banco de dados (PostgreSQL). Se omitida, usa SQLite local | Não |

## Deploy

A aplicação está preparada para deploy com Gunicorn através do `Procfile`:

```
web: gunicorn "app:create_app('production')" --workers 2 --bind 0.0.0.0:$PORT
```

Para isso, configure no serviço de hospedagem (ex.: Railway, Render) as variáveis `SECRET_KEY`, `DATABASE_URL` e `FLASK_ENV=production`, e execute `flask db upgrade` após o primeiro deploy para criar as tabelas.