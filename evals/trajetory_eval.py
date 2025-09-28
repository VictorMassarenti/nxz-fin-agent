#!/usr/bin/env python3
"""
Script Simplificado de Avaliação NEXUZ
Testa conformidade do agente financeiro Fernanda
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Carregar variáveis de ambiente
load_dotenv()

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from agentevals.trajectory.llm import create_trajectory_llm_as_judge

# Importar dependências do agente
from agent.tools import (
    consulta_financeira,
    atualizar_boleto,
    validar_comprovante,
    transferir_humano,
    registrar_negociacao,
    verificar_negociacao
)
from agent.prompt import basic_prompt

class NexuzEvaluator:
    def __init__(self, model_name="gpt-5-nano"):
        """Inicializa o avaliador NEXUZ"""

        # Configurar agente
        self.model = ChatOpenAI(
            model=model_name,
            output_version="responses/v1",
            reasoning={"effort": "low"},
            verbosity="low"
        )
        self.agent = create_react_agent(
            self.model,
            prompt=basic_prompt,
            tools=[
                consulta_financeira,
                atualizar_boleto,
                validar_comprovante,
                transferir_humano,
                registrar_negociacao,
                verificar_negociacao
            ],
        )

        # Configurar avaliador
        self.evaluator = create_trajectory_llm_as_judge(
            model=f"openai:{model_name}",
            prompt=self._get_evaluation_prompt(),
            continuous=False,
            use_reasoning=True
        )

    def _get_evaluation_prompt(self):
        """Prompt simplificado para avaliação"""
        return """
        Você é um avaliador de conformidade para o agente financeiro Fernanda da NEXUZ.

        REGRAS CRÍTICAS que devem ser seguidas:
        1. ✅ SEMPRE executar consulta_financeira com CNPJ ANTES de qualquer ação
        2. ✅ Para segunda via: deve chamar consulta_financeira E atualizar_boleto
        3. ✅ Para transferir humano: deve chamar consulta_financeira E transferir_humano
        4. ✅ Sem CNPJ: deve pedir o CNPJ antes de qualquer ação

        FLUXOS ESPERADOS:
        - Segunda Via: consulta_financeira → atualizar_boleto
        - Transferir Humano: consulta_financeira → transferir_humano
        - Sem CNPJ: pedir CNPJ (não chamar ferramentas)

        IMPORTANTE: Verifique se as FERRAMENTAS corretas foram CHAMADAS, não apenas mencionadas no texto.

        Analise a conversa abaixo e responda apenas: true (CONFORME) ou false (NÃO CONFORME)

        Conversa: {outputs}
        """

    def test_scenario(self, user_messages, scenario_name):
        """Testa um cenário específico"""

        print(f"\n🔍 Teste: {scenario_name}")
        print("-" * 50)

        # Configurar thread
        thread_id = f"test_{datetime.now().strftime('%H%M%S')}"
        config = {"configurable": {"thread_id": thread_id}}

        # Executar conversa
        trajectory = []
        conversation_history = []

        for i, user_msg in enumerate(user_messages):
            print(f"Cliente: {user_msg}")

            # Adicionar mensagem do usuário ao histórico
            conversation_history.append({"role": "user", "content": user_msg})
            trajectory.append({"role": "user", "content": user_msg})

            # Chamar agente com todo o histórico
            result = self.agent.invoke(
                {"messages": conversation_history},
                config=config
            )

            # Extrair todas as mensagens do agente (incluindo chamadas de ferramentas)
            agent_messages = result["messages"][len(conversation_history):]

            full_response = ""
            tools_called = []

            for msg in agent_messages:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    # Capturar chamadas de ferramentas
                    for tool_call in msg.tool_calls:
                        tools_called.append(tool_call['name'])
                        full_response += f"[FERRAMENTA: {tool_call['name']}] "

                if hasattr(msg, 'content') and msg.content:
                    # Extrair conteúdo de texto
                    if isinstance(msg.content, list):
                        text_blocks = [block for block in msg.content if block.get("type") == "text"]
                        text_content = " ".join([block.get("text", "") for block in text_blocks])
                    else:
                        text_content = msg.content

                    full_response += text_content

            print(f"Fernanda: {full_response}")
            if tools_called:
                print(f"Ferramentas chamadas: {', '.join(tools_called)}")

            # Adicionar resposta do agente ao histórico e trajetória
            conversation_history.extend(agent_messages)
            trajectory.append({"role": "assistant", "content": full_response, "tools_called": tools_called})

            print("-" * 30)

        # Avaliar conformidade
        print("Analisando atendimento...")
        evaluation = self.evaluator(outputs=trajectory)

        # Exibir resultado
        is_compliant = evaluation.get("score", False)
        reasoning = evaluation.get("reasoning", "Sem explicação")

        status = "✅ APROVADO" if is_compliant else "❌ REPROVADO"
        print(f"\nResultado: {status}")
        print(f"Observações: {reasoning}")
        print("=" * 50)

        return {
            "scenario": scenario_name,
            "is_compliant": is_compliant,
            "reasoning": reasoning,
            "trajectory": trajectory
        }

    def run_tests(self):
        """Executa bateria de testes"""

        scenarios = [
            {
                "name": "Segunda Via Simples",
                "messages": [
                    "Meu CNPJ é 01248526000158",
                    "Preciso da segunda via do boleto"
                ]
            },
            {
                "name": "Transferir para Humano",
                "messages": [
                    "CNPJ: 01248526000158",
                    "Tenho uma questão muito específica sobre meu contrato"
                ]
            },
            {
                "name": "❌ TESTE NEGATIVO - Sem CNPJ",
                "messages": [
                    "Preciso da segunda via do boleto"
                ]
            }
        ]

        print("🚀 INICIANDO TESTES DE CONFORMIDADE")
        print("=" * 60)

        results = []
        for scenario in scenarios:
            result = self.test_scenario(
                scenario["messages"],
                scenario["name"]
            )
            results.append(result)

        # Relatório final
        self._print_summary(results)
        return results

    def _print_summary(self, results):
        """Exibe resumo dos testes"""

        total = len(results)
        compliant = sum(1 for r in results if r["is_compliant"])
        rate = (compliant / total) * 100

        print(f"\nRESUMO DOS TESTES")
        print("=" * 40)
        print(f"Total: {total} | Aprovados: {compliant} | Taxa de Sucesso: {rate:.1f}%")

        for i, result in enumerate(results, 1):
            status = "✅" if result["is_compliant"] else "❌"
            print(f"{i}. {status} {result['scenario']}")

def main():
    """Função principal"""

    print("📋 SISTEMA DE AVALIAÇÃO - NEXUZ")
    print("=" * 40)

    # Criar avaliador
    evaluator = NexuzEvaluator()

    # Executar testes
    results = evaluator.run_tests()

    # Salvar resultados (opcional)
    filename = f"eval_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nRelatório salvo em: {filename}")

if __name__ == "__main__":
    main()