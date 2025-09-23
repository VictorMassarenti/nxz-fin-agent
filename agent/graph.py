from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from agent.tools import consulta_financeira, atualizar_boleto, processar_comprovante, transferir_humano, _db_url
from agent.prompt import system_message

model = ChatOpenAI(
    model="gpt-5-nano",
    output_version="responses/v1",
    reasoning={"effort": "low"},
    verbosity="low",
)

agent = create_react_agent(model, prompt=system_message, tools=[consulta_financeira, atualizar_boleto, processar_comprovante, transferir_humano])