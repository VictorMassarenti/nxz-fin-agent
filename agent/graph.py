from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from agent.tools import (
    consulta_financeira,
    atualizar_boleto,
    validar_comprovante,
    transferir_humano,
    registrar_negociacao,
    verificar_negociacao
)
from agent.prompt import system_message, basic_prompt

model = ChatOpenAI(
    model="gpt-5-nano",
    output_version="responses/v1",
    reasoning={"effort": "low"},
    verbosity="low",
)

agent = create_react_agent(
    model,
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
