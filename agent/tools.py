from datetime import datetime, timedelta
import uuid

from langchain_core.tools import tool

from agent.models import (
    ConsultaFinanceiraInput,
    ConsultaFinanceiraOutput,
    AtualizarBoletoInput,
    AtualizarBoletoOutput,
    RegistrarNegociacaoInput,
    RegistrarNegociacaoOutput,
    VerificarNegociacaoInput,
    VerificarNegociacaoOutput,
    ValidarComprovanteInput,
    ValidarComprovanteOutput,
    TransferirHumanoInput,
    TransferirHumanoOutput,
)
from agent.utils import _conn, _get_asaas_config, _handle_asaas_request

@tool
def consulta_financeira(input: ConsultaFinanceiraInput) -> ConsultaFinanceiraOutput:
    """Busca informações de um cliente e suas pendências no Asaas pelo CNPJ.

    Args:
        input: Dados de entrada contendo o CNPJ do cliente

    Returns:
        ConsultaFinanceiraOutput: Informações do cliente e suas pendências
    """
    # Obter configuração da API do Asaas
    config, error = _get_asaas_config()
    if error:
        return ConsultaFinanceiraOutput(**error)

    base_url = config["base_url"]
    headers = config["headers"]

    # Primeiro passo: Buscar o cliente pelo CNPJ
    customer_url = f"{base_url}/customers"
    customer_params = {"cpfCnpj": input.cnpj}

    customer_data, error = _handle_asaas_request(
        "GET", customer_url, headers, params=customer_params
    )
    if error:
        return ConsultaFinanceiraOutput(**error)

    # Verificar se encontrou o cliente
    total_count = customer_data.get("totalCount", 0)
    data = customer_data.get("data")

    if total_count <= 0 or not data:
        return ConsultaFinanceiraOutput(
            status="nao_encontrado",
            mensagem="Cliente não encontrado no Asaas",
        )

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
        return ConsultaFinanceiraOutput(**error)

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
    return ConsultaFinanceiraOutput(
        status="sucesso",
        cliente={
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
        pendencias=pendencias,
        total_pendencias=len(pendencias),
    )


@tool
def atualizar_boleto(input: AtualizarBoletoInput) -> AtualizarBoletoOutput:
    """Atualiza um boleto existente no Asaas, definindo nova data de vencimento para 3 dias a partir de hoje.
    O desconto é aplicado automaticamente por ser antecipação do vencimento (desconto de juros).

    Args:
        input: Dados de entrada contendo boleto_id e valor

    Returns:
        AtualizarBoletoOutput: Informações do boleto atualizado
    """
    # Obter configuração da API do Asaas
    config, error = _get_asaas_config()
    if error:
        return AtualizarBoletoOutput(**error)

    base_url = config["base_url"]
    headers = config["headers"]

    # Calcular nova data de vencimento (data atual + 3 dias)
    nova_data_vencimento = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    # Dados para atualização do boleto
    update_data = {
        "value": input.valor,
        "dueDate": nova_data_vencimento,
        "billingType": "UNDEFINED",
    }

    # Atualizar o pagamento via API PUT
    payment_url = f"{base_url}/payments/{input.boleto_id}"
    updated_payment, error = _handle_asaas_request(
        "PUT", payment_url, headers, json=update_data
    )
    if error:
        return AtualizarBoletoOutput(**error)

    # Retornar informações do boleto atualizado
    return AtualizarBoletoOutput(
        status="sucesso",
        boleto_id=updated_payment.get("id"),
        valor=updated_payment.get("value"),
        data_vencimento=updated_payment.get("dueDate"),
        data_vencimento_original=updated_payment.get("originalDueDate"),
        link_boleto=updated_payment.get("bankSlipUrl"),
        link_fatura=updated_payment.get("invoiceUrl"),
        numero_fatura=updated_payment.get("invoiceNumber"),
        status_pagamento=updated_payment.get("status"),
    )


@tool
def registrar_negociacao(input: RegistrarNegociacaoInput) -> RegistrarNegociacaoOutput:
    """Registra uma negociação feita com o cliente, salvando os detalhes no banco de dados.

    Args:
        input: Dados de entrada contendo CNPJ e detalhes da negociação

    Returns:
        RegistrarNegociacaoOutput: Status da operação
    """
    if not input.cnpj or input.cnpj.strip() == "":
        return RegistrarNegociacaoOutput(
            status="erro",
            mensagem="CNPJ é obrigatório para registrar a negociação"
        )

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO negociacoes (cnpj, detalhes) VALUES (%s, %s)",
                (input.cnpj, input.detalhes),
            )
            conn.commit()
    return RegistrarNegociacaoOutput(
        status="sucesso",
        mensagem="Negociação registrada com sucesso"
    )


@tool
def verificar_negociacao(input: VerificarNegociacaoInput) -> VerificarNegociacaoOutput:
    """Busca as negociações registradas para um CNPJ específico no banco de dados.

    Args:
        input: Dados de entrada contendo o CNPJ

    Returns:
        VerificarNegociacaoOutput: Lista de negociações encontradas
    """
    if not input.cnpj or input.cnpj.strip() == "":
        return VerificarNegociacaoOutput(
            status="erro",
            mensagem="CNPJ é obrigatório para verificar negociações"
        )

    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, cnpj, detalhes, data_criacao FROM negociacoes WHERE cnpj = %s ORDER BY data_criacao DESC",
                    (input.cnpj,)
                )
                negociacoes = cur.fetchall()

        if not negociacoes:
            return VerificarNegociacaoOutput(
                status="nao_encontrado",
                mensagem="Nenhuma negociação encontrada para este CNPJ"
            )

        negociacoes_list = []
        for neg in negociacoes:
            negociacoes_list.append({
                "id": neg[0],
                "cnpj": neg[1],
                "detalhes": neg[2],
                "data_criacao": neg[3].isoformat() if neg[3] else None
            })

        return VerificarNegociacaoOutput(
            status="sucesso",
            negociacoes=negociacoes_list,
            total=len(negociacoes_list)
        )

    except Exception as e:
        return VerificarNegociacaoOutput(
            status="erro",
            mensagem=f"Erro ao buscar negociações: {str(e)}"
        )


@tool
def validar_comprovante(input: ValidarComprovanteInput) -> ValidarComprovanteOutput:
    """Valida o texto pós OCR do documento enviado.
    Retorna se o comprovante é válido ou não e a taxa de confiabilidade.

    Args:
        input: Dados de entrada contendo o texto do OCR

    Returns:
        ValidarComprovanteOutput: Resultado da validação
    """
    print(input.ocr_text)

    # TODO: Implementar lógica de validação real
    return ValidarComprovanteOutput(
        status="sucesso",
        mensagem="Comprovante processado com sucesso",
        valido=True,
        confiabilidade=0.95
    )


@tool
def transferir_humano(input: TransferirHumanoInput) -> TransferirHumanoOutput:
    """Transfere o atendimento para um humano, preservando o contexto.

    Args:
        input: Dados de entrada contendo o contexto da conversa

    Returns:
        TransferirHumanoOutput: Confirmação da transferência com ticket_id
    """
    print(input.contexto)

    # Simulando geração de ticket
    ticket_id = str(uuid.uuid4())[:8]

    return TransferirHumanoOutput(
        status="sucesso",
        mensagem="Atendimento transferido para um humano com sucesso",
        ticket_id=ticket_id
    )

# Provavelmente um help desk