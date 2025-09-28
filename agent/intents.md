# Intents do Agente Financeiro NEXUZ (Fernanda)

> Intent é a ação de negócio final que o agente financeiro executa. Fernanda é especializada em atendimento financeiro do setor Food Service, com foco em validação de clientes, consultas de débitos, geração de segunda via e processamento de comprovantes.

## Consulta Financeira
- intent: `cliente_validar`
  - tool: `consulta_financeira`
  - exemplos: "CNPJ 12.345.678/0001-90", "Meu CNPJ é 22.333.444/0001-55"
  - data: `{ cliente: {...}, pendencias: [...], total_pendencias, status }`
  - **OBRIGATÓRIO**: Sempre executar no início após receber CNPJ

## Segunda Via de Boleto
- intent: `boleto_gerar_segunda_via`
  - tool: `atualizar_boleto`
  - exemplos: "Preciso da segunda via", "Gerar novo boleto", "Fatura atualizada"
  - data: `{ message: "link-para-segunda-via" }`
  - **Regra**: Se primeira negociação → atualizar boleto, desconto é automático pela ferramenta. (3 dias úteis o vencimento)
- intent: `boleto_primeira_negociacao`
  - tool: `atualizar_boleto` + desconto
  - exemplos: "Primeira vez negociando", "Nunca paguei em atraso antes"
  - data: `{ message: "link-com-desconto", validade: "3 dias úteis" }`

## Processamento de Comprovante
- intent: `comprovante_validar`
  - tool: `validar_comprovante`
  - exemplos: "Segue o comprovante", "Aqui está o PIX", "PDF do pagamento"
  - data: `{ message: "status_validacao", confiabilidade: "%" }`
  - **Formatos**: Receberá o texto pós processamento OCR
- intent: `comprovante_solicitar_novo`
  - tool: (análise) → solicitar reenvio
  - exemplos: "Comprovante ilegível", "Valor divergente", "Data incorreta"
  - data: `{ status: "rejeitado", motivo: "..." }`

## Negociação e Registro
- intent: `negociacao_registrar`
  - tool: `registrar_negociacao`
  - exemplos: "Cliente teve seu boleto atualizado", "Atualizado boleto para pagamento"
  - data: `{ message: "Negociação registrada com sucesso" }`
- intent: `negociacao_primeira_vez`
  - tool: `verificar_negociacao`
  - exemplos: "É minha primeira negociação", "Nunca atrasei antes"
  - data: `{ elegivel_desconto: true/false }`

## Escalação para Humano
- intent: `transferir_atendimento`
  - tool: `transferir_humano`
  - exemplos: "Quero falar com alguém", "Preciso de ajuda especializada"
  - data: `{ message: "Atendimento transferido", contexto: "..." }`
  - **Cenários**: negociações especiais, problemas técnicos complexos, cliente agressivo, fora do escopo financeiro

## Suporte e Informações
- intent: `status_cliente_consultar`
  - tool: `consulta_financeira` + análise
  - exemplos: "Como está minha situação?", "Tenho débitos?"
  - data: `{ status: "ATIVO/BLOQUEADO/EM_ATRASO", resumo_situacao }`
- intent: `suporte_tecnico_negado`
  - tool: (verificação) → mensagem informativa
  - exemplos: "Sistema não funciona" (cliente inadimplente)
  - data: `{ message: "Regularize débitos primeiro" }`

## Utilidades e Validações
- intent: `cnpj_invalido`
  - tool: (validação) → solicitar correção
  - exemplos: "CNPJ incorreto", "Formato inválido"
  - data: `{ status: "erro", message: "CNPJ inválido" }`
- intent: `cliente_nao_encontrado`
  - tool: `consulta_financeira` → status "nao_encontrado"
  - exemplos: "Cliente não cadastrado"
  - data: `{ status: "nao_encontrado", message: "Cliente não encontrado" }`

## Finalização de Atendimento
- intent: `atendimento_finalizar`
  - tool: (nenhuma) → mensagem padrão
  - exemplos: Após resolver solicitação com sucesso
  - data: `{ message: "Posso ajudar com mais alguma coisa? 😊" }`
  - **Regra**: Usar APENAS após resolver completamente a solicitação

## Cenários → Intents Esperadas (fluxos principais)

### Cenário A (Validação + Segunda Via)
1. `cliente_validar` → 2. `boleto_gerar_segunda_via` → 3. `atendimento_finalizar`

### Cenário B (Primeira Negociação com Desconto)
1. `cliente_validar` → 2. `negociacao_primeira_vez` → 3. `boleto_primeira_negociacao` → 4. `negociacao_registrar` → 5. `atendimento_finalizar`

### Cenário C (Validação de Comprovante)
1. `cliente_validar` → 2. `comprovante_validar` → 3. `atendimento_finalizar`

### Cenário D (Escalação para Humano)
1. `cliente_validar` → 2. `transferir_atendimento`

### Cenário E (Cliente Inadimplente + Suporte Técnico)
1. `cliente_validar` → 2. `suporte_tecnico_negado`

## Regras de Negócio Críticas
- **NUNCA** prosseguir sem validar CNPJ via `consulta_financeira`
- **NUNCA** oferecer desconto
- **NUNCA** dar suporte técnico para clientes inadimplentes
- **SEMPRE** usar `atendimento_finalizar` após resolver solicitação
- **SEMPRE** preservar contexto ao transferir para humano