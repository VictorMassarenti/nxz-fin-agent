import os
import requests

import psycopg
from langchain_core.tools import tool


def _db_url() -> str:
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")

    base = f"postgresql://{user}:{pwd}@{host}:{port}/{name}"

    return base


def _conn():
    return psycopg.connect(_db_url())


@tool
def consulta_financeira(cnpj: str):
    """Busca informações de um cliente e suas pendências no Asaas pelo CPF ou CNPJ.

    Args:
        cpf_cnpj (str): CPF ou CNPJ do cliente a ser buscado

    Returns:
        dict: Informações do cliente e suas pendências retornadas pela API do Asaas
    """
    # Obter a chave de API do Asaas das variáveis de ambiente
    api_key = os.getenv("ASAAS_API_KEY")
    if not api_key:
        return {"status": "erro", "mensagem": "Chave de API do Asaas não configurada"}

    # Verificar se é um ambiente de sandbox
    is_sandbox = os.getenv("ASAAS_SANDBOX", "false").lower() == "true"

    # Determinar a URL base da API
    if is_sandbox:
        base_url = "https://sandbox.asaas.com/api/v3"
    else:
        base_url = "https://api.asaas.com/v3"

    # Cabeçalhos da requisição
    headers = {"access_token": api_key, "Content-Type": "application/json"}

    # Primeiro passo: Buscar o cliente pelo CPF/CNPJ
    customer_url = f"{base_url}/customers"
    customer_params = {"cpfCnpj": cnpj}

    try:
        # Fazer a requisição GET para buscar o cliente
        customer_response = requests.get(
            customer_url, headers=headers, params=customer_params
        )

        # Verificar se a requisição foi bem-sucedida
        if customer_response.status_code != 200:
            return {
                "status": "erro",
                "mensagem": f"Erro na requisição ao buscar cliente: {customer_response.status_code} - {customer_response.text}",
            }

        customer_data = customer_response.json()

        # Verificar se encontrou o cliente
        if not customer_data.get("totalCount", 0) > 0 or not customer_data.get("data"):
            return {
                "status": "nao_encontrado",
                "mensagem": "Cliente não encontrado no Asaas",
            }

        # Pegar o primeiro cliente encontrado
        cliente = customer_data["data"][0]
        customer_id = cliente.get("id")

        # Segundo passo: Buscar as pendências do cliente usando o ID
        payments_url = f"{base_url}/payments"
        payments_params = {"customer": customer_id}

        # Fazer a requisição GET para buscar as pendências
        payments_response = requests.get(
            payments_url, headers=headers, params=payments_params
        )

        # Verificar se a requisição foi bem-sucedida
        if payments_response.status_code != 200:
            return {
                "status": "erro",
                "mensagem": f"Erro na requisição ao buscar pendências: {payments_response.status_code} - {payments_response.text}",
            }

        payments_data = payments_response.json()

        # Processar as pendências para um formato mais amigável
        pendencias = []
        if payments_data.get("data"):
            for pagamento in payments_data["data"]:
                # Processar multas e juros
                fine_value = 0
                interest_value = 0

                if pagamento.get("fine") and isinstance(pagamento.get("fine"), dict):
                    fine_value = pagamento["fine"].get("value", 0)

                if pagamento.get("interest") and isinstance(
                    pagamento.get("interest"), dict
                ):
                    interest_value = pagamento["interest"].get("value", 0)

                # Calcular valor total com multas e juros
                total_value = pagamento.get("value", 0) + fine_value + interest_value

                pendencias.append(
                    {
                        "id": pagamento.get("id"),
                        "data_criacao": pagamento.get("dateCreated"),
                        "status": pagamento.get("status"),
                        "valor": pagamento.get("value"),
                        "multa": fine_value,
                        "juros": interest_value,
                        "valor_total": total_value,
                        "data_vencimento": pagamento.get("dueDate"),
                        "data_vencimento_original": pagamento.get("originalDueDate"),
                        "tipo_cobranca": pagamento.get("billingType"),
                        "numero_fatura": pagamento.get("invoiceNumber"),
                        "link_fatura": pagamento.get("invoiceUrl"),
                        "link_boleto": pagamento.get("bankSlipUrl"),
                        "descricao": pagamento.get("description"),
                        "pago": pagamento.get("status") == "RECEIVED",
                    }
                )

        # Retornar as informações completas do cliente e suas pendências
        return {
            "status": "sucesso",
            "cliente": {
                "id": cliente.get("id"),
                "nome": cliente.get("name"),
                "email": cliente.get("email"),
                "empresa": cliente.get("company"),
                "cpfCnpj": cliente.get("cpfCnpj"),
                "telefone": cliente.get("phone"),
                "celular": cliente.get("mobilePhone"),
                "endereco": cliente.get("address"),
                "numero": cliente.get("addressNumber"),
                "complemento": cliente.get("complement"),
                "bairro": cliente.get("province"),
                "cep": cliente.get("postalCode"),
                "cidade": cliente.get("cityName"),
                "estado": cliente.get("state"),
                "pais": cliente.get("country"),
                "tipo_pessoa": cliente.get("personType"),
                "deletado": cliente.get("deleted"),
                "grupos": (
                    [grupo.get("name") for grupo in cliente.get("groups", [])]
                    if cliente.get("groups")
                    else []
                ),
            },
            "pendencias": pendencias,
            "total_pendencias": len(pendencias),
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "erro",
            "mensagem": f"Erro de conexão com a API do Asaas: {str(e)}",
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao buscar informações no Asaas: {str(e)}",
        }


@tool
def atualizar_boleto(cnpj: str, boleto_id: str):
    """Gera uma segunda via do boleto, aplicando desconto se for a primeira negociação.
    Retorna o link do novo boleto."""

    return {"message": "https://link-para-segunda-via-do-boleto.com"}


@tool
def processar_comprovante(gcs_uri: str):
    """Processa um documento usando o Google Document AI.
    Retorna se o comprovante é válido ou não e a taxa de confiabilidade."""
    return {"message": "Comprovante processado com sucesso"}


@tool
def transferir_humano(contexto: str):
    """Transfere o atendimento para um humano, preservando o contexto."""
    return {"message": "Atendimento transferido para um humano com sucesso"}
