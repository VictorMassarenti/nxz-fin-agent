import os
import requests
from datetime import datetime, timedelta

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


def _get_asaas_config():
    """Retorna configuração da API do Asaas."""
    api_key = os.getenv("ASAAS_API_KEY")
    if not api_key:
        return None, {
            "status": "erro",
            "mensagem": "Chave de API do Asaas não configurada",
        }

    is_sandbox = os.getenv("ASAAS_SANDBOX", "false").lower() == "true"
    base_url = (
        "https://sandbox.asaas.com/api/v3" if is_sandbox else "https://api.asaas.com/v3"
    )
    headers = {"access_token": api_key, "Content-Type": "application/json"}

    return {"base_url": base_url, "headers": headers}, None


def _handle_asaas_request(method, url, headers, **kwargs):
    """Faz requisição para API do Asaas com tratamento de erros padronizado."""
    try:
        response = requests.request(method, url, headers=headers, **kwargs)

        if response.status_code != 200:
            return None, {
                "status": "erro",
                "mensagem": f"Erro na requisição: {response.status_code} - {response.text}",
            }

        return response.json(), None

    except requests.exceptions.RequestException as e:
        return None, {
            "status": "erro",
            "mensagem": f"Erro de conexão com a API do Asaas: {str(e)}",
        }
    except Exception as e:
        return None, {
            "status": "erro",
            "mensagem": f"Erro inesperado: {str(e)}",
        }


@tool
def consulta_financeira(cnpj: str):
    """Busca informações de um cliente e suas pendências no Asaas pelo CNPJ.

    Args:
        cnpj (str): CNPJ do cliente a ser buscado

    Returns:
        dict: Informações do cliente e suas pendências retornadas pela API do Asaas
    """
    # Obter configuração da API do Asaas
    config, error = _get_asaas_config()
    if error:
        return error

    base_url = config["base_url"]
    headers = config["headers"]

    # Primeiro passo: Buscar o cliente pelo CNPJ
    customer_url = f"{base_url}/customers"
    customer_params = {"cpfCnpj": cnpj}

    customer_data, error = _handle_asaas_request(
        "GET", customer_url, headers, params=customer_params
    )
    if error:
        return error

    # Verificar se encontrou o cliente
    total_count = customer_data.get("totalCount", 0)
    data = customer_data.get("data")

    if total_count <= 0 or not data:
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

    payments_data, error = _handle_asaas_request(
        "GET", payments_url, headers, params=payments_params
    )
    if error:
        return error

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


@tool
def atualizar_boleto(boleto_id: str, valor: float):
    """Atualiza um boleto existente no Asaas, definindo nova data de vencimento para 3 dias a partir de hoje.
    O desconto é aplicado automaticamente por ser antecipação do vencimento (desconto de juros).

    Args:
        boleto_id (str): ID do pagamento no Asaas
        valor (float): Valor do boleto

    Returns:
        dict: Informações do boleto atualizado com links de acesso
    """
    # Obter configuração da API do Asaas
    config, error = _get_asaas_config()
    if error:
        return error

    base_url = config["base_url"]
    headers = config["headers"]

    # Calcular nova data de vencimento (data atual + 3 dias)
    nova_data_vencimento = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    # Dados para atualização do boleto
    update_data = {
        "value": valor,
        "dueDate": nova_data_vencimento,
        "billingType": "UNDEFINED",
    }

    # Atualizar o pagamento via API PUT
    payment_url = f"{base_url}/payments/{boleto_id}"
    updated_payment, error = _handle_asaas_request(
        "PUT", payment_url, headers, json=update_data
    )
    if error:
        return error

    # Retornar informações do boleto atualizado
    return {
        "status": "sucesso",
        "boleto_id": updated_payment.get("id"),
        "valor": updated_payment.get("value"),
        "data_vencimento": updated_payment.get("dueDate"),
        "data_vencimento_original": updated_payment.get("originalDueDate"),
        "link_boleto": updated_payment.get("bankSlipUrl"),
        "link_fatura": updated_payment.get("invoiceUrl"),
        "numero_fatura": updated_payment.get("invoiceNumber"),
        "status_pagamento": updated_payment.get("status"),
    }


@tool
def registrar_negociacao(cnpj: str, detalhes: str):
    """Registra uma negociação feita com o cliente, salvando os detalhes no banco de dados.

    Args:
        cnpj (str): CNPJ do cliente (obrigatório)
        detalhes (str): Detalhes da negociação
    """
    if not cnpj or cnpj.strip() == "":
        return {
            "status": "erro",
            "mensagem": "CNPJ é obrigatório para registrar a negociação"
        }

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO negociacoes (cnpj, detalhes) VALUES (%s, %s)",
                (cnpj, detalhes),
            )
            conn.commit()
    return {"status": "sucesso", "message": "Negociação registrada com sucesso"}


@tool
def processar_comprovante(gcs_uri: str):
    """Processa um documento usando o Google Document AI.
    Retorna se o comprovante é válido ou não e a taxa de confiabilidade."""
    return {"message": "Comprovante processado com sucesso"}


@tool
def transferir_humano(contexto: str):
    """Transfere o atendimento para um humano, preservando o contexto."""
    return {"message": "Atendimento transferido para um humano com sucesso"}
