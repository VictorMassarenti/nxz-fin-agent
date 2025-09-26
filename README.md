# NXZ Fin Agent - Fernanda

Agente financeiro inteligente da NEXUZ, especializado em atendimento automatizado para o setor Food Service. Fernanda é capaz de validar clientes, consultar débitos, gerar segundas vias de boletos e validar comprovantes de pagamento de forma autônoma.

## 🎯 Funcionalidades

- **Validação de Clientes**: Consulta automática de dados via CNPJ
- **Gestão de Boletos**: Geração de segundas vias com descontos automáticos
- **Validação de Comprovantes**: Processamento de documentos via OCR
- **Negociações**: Registro e histórico de negociações com clientes
- **Escalação Humana**: Transferência inteligente para atendentes humanos (implementar)
- **Integração Asaas**: API completa para gestão financeira

## 🏗️ Arquitetura

O projeto utiliza LangGraph para orquestração de agentes inteligentes, integrado com:

- **LangChain/LangGraph**: Orquestração de sistemas agênticos
- **OpenAI GPT**: Modelo de linguagem principal
- **PostgreSQL**: Banco de dados para negociações
- **Asaas API**: Plataforma de pagamentos
- **Document AI**: OCR para validação de comprovantes

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL
- Conta Asaas (sandbox ou produção)
- Chaves de API configuradas

## 🚀 Instalação

1. Clone o repositório:

```bash
git clone https://github.com/nexuz/nxz-fin-agent.git
cd nxz-fin-agent
```

2. Crie um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\Activate.ps1     # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## ⚙️ Configuração

Configure as seguintes variáveis no arquivo `.env`:

```env
# Banco de Dados (Pooler)
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=6543
DB_NAME=nxz_fin_agent

# Asaas API
ASAAS_API_KEY=sua_chave_api
ASAAS_SANDBOX=true  # false para produção

# OpenAI
OPENAI_API_KEY=sua_chave_openai
```

## 🏃‍♂️ Execução

### Desenvolvimento Local

```bash
# Inicie o agente
langgraph dev # Linux/Mac

langgraph dev --allow-blocking # Windows
```

### Deploy com LangGraph Platform

```bash
# Deploy para produção
langgraph deploy
```

## 🛠️ Ferramentas Disponíveis

### consulta_financeira(cnpj)

Busca informações completas do cliente no Asaas pelo CNPJ, incluindo dados pessoais e pendências financeiras.

### atualizar_boleto(boleto_id, valor)

Gera segunda via de boleto com nova data de vencimento (3 dias) e aplica desconto automático (retira o juros).

### validar_comprovante(ocr_text)

Valida a partir do texto extraído de comprovantes de pagamento enviados pelos clientes.

### registrar_negociacao(cnpj, detalhes)

Registra histórico de negociações no banco de dados.

### verificar_negociacao(cnpj)

Consulta negociações anteriores para determinar elegibilidade a descontos.

### transferir_humano(contexto)

Escala atendimento para humanos preservando todo o contexto da conversa.

## 📊 Regras de Negócio

- ✅ **Validação obrigatória**: Sempre validar CNPJ antes de qualquer ação
- 🎁 **Desconto primeira negociação**: 5% de desconto válido por 3 dias úteis
- 🚫 **Sem desconto segunda negociação**: Boletos sem desconto após primeira negociação
- 🔒 **Suporte técnico restrito**: Não oferecido para clientes inadimplentes
- 📝 **Registro obrigatório**: Todas as negociações devem ser registradas

## 🧪 Testes

```bash
# Execute os testes
python -m pytest tests/

# Testes com cobertura
python -m pytest tests/ --cov=agent
```

## 📁 Estrutura do Projeto

```
nxz-fin-agent/
├── agent/
│   ├── graph.py          # Configuração do agente LangGraph
│   ├── tools.py          # Ferramentas e integrações
│   └── prompt.py         # Prompts e configurações
├── tests/                # Testes automatizados
├── scripts/              # Scripts auxiliares
├── sql/                  # Schemas do banco de dados
├── evals/                # Avaliações e métricas
├── requirements.txt      # Dependências Python
├── langgraph.json        # Configuração LangGraph
└── .env                  # Variáveis de ambiente
```

## 🎯 Intents Suportados

- `cliente_validar`: Validação de dados do cliente
- `boleto_gerar_segunda_via`: Geração de segunda via
- `boleto_primeira_negociacao`: Primeira negociação com desconto
- `comprovante_validar`: Validação de comprovantes
- `negociacao_registrar`: Registro de negociações
- `transferir_atendimento`: Escalação para humanos
- `status_cliente_consultar`: Consulta de situação financeira

## 📈 Métricas e Monitoramento

O projeto utiliza LangSmith para:

- Tracing de conversas
- Métricas de desempenho
- Análise de qualidade das respostas
- Monitoramento de custos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

**Fernanda** - Transformando atendimento financeiro com inteligência artificial 🤖✨
