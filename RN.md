RN01 - cada câmera representa uma mão de obra

RN02 -  Valores recorrentes vêm de planos de Starlink e Câmera

RN03 - Cada custo tem a si uma parcela associada, sendo o pix parcela única e cartãod e crédito o número de parcelas da compra original

"""
Clientes
CRUD Clientes
Criar cliente
Ler clientes
Atualizar clientes
Excluir clientes

Orçamento
Página de Orçamento
tipo | câmera, cerca, elétrica, etc.
descrição

	ItensOrcamento
	id
	tipo_item
	quantidade
	valor_unitário
	medida
Tabela de histórico do status para saber o quanto tempo cada orçamento passa em cada status. Ex: ficou 10 dias como rascunho, 5 como enviado, 2 aprovado.

Gastos
CRUD Gastos
Criar gastos
Ler gastos
Atualizar gastos
Excluir gastos
tipo pagamento
1. Tabela de gastos
2. tabela de parcelas (cada uma tem sua data de vencimento e data de pagamento)

Starlink
há muitas starlinks, o objetivo é que se tenha um controle delas, no sentido de saber quem é o dono dela, qual a situação do plano, se ela está ativa ou não, e se o dono deve algo da starlink para a gente;

"""


5. BaseModel x db.Model

Você mistura:

class Orcamento(BaseModel):

e

class ItemOrcamento(db.Model):

Isso pode ser inconsistente.

Se o BaseModel possui:

created_at
updated_at
id

Então o ideal seria:

class ItemOrcamento(BaseModel):

para manter o padrão.