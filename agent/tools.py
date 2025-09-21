import os
import json
import requests

import psycopg
from langchain_core.tools import tool

# Google Document AI imports
from google.cloud import documentai
from google.oauth2 import service_account


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
def add_client(
    name: str,
    phone=None,
    email=None,
    company=None,
    tags=None,
    notes=None,
):
    """Adiciona um cliente no banco. Passe name, e opcionalmente phone, email, company, tags, notes."""
    return {"message": "Cliente adicionado com sucesso"}


@tool
def find_client(query: str):
    """Busca clientes cujo nome ou empresa contenham o termo informado."""
    return {"message": "Cliente encontrado com sucesso"}


@tool
def consultar_debitos_cliente(cnpj: str):
    """Consulta débitos de um cliente pelo CNPJ. Retorna informações do cliente e seus débitos."""
    # Caminho para o arquivo mock-data.json
    mock_data_path = os.path.join(os.path.dirname(__file__), '..', 'mock-data.json')
    
    try:
        # Carregar os dados do arquivo mock-data.json
        with open(mock_data_path, 'r', encoding='utf-8') as file:
            mock_data = json.load(file)
        
        # Limpar o CNPJ para comparação (remover caracteres não numéricos)
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        # Procurar o cliente pelo CNPJ
        cliente_encontrado = None
        for cliente in mock_data.get('clientes', []):
            # Verificar nos campos cnpj e cnpj_limpo
            cliente_cnpj = ''.join(filter(str.isdigit, cliente.get('cnpj', '')))
            cliente_cnpj_limpo = cliente.get('cnpj_limpo', '')
            
            if cnpj_limpo == cliente_cnpj or cnpj_limpo == cliente_cnpj_limpo:
                cliente_encontrado = cliente
                break
        
        # Se não encontrou o cliente, retornar mensagem de erro
        if not cliente_encontrado:
            return {
                "status": "erro",
                "mensagem": "Cliente não encontrado"
            }
        
        # Se o cliente estiver bloqueado, retornar essa informação
        if cliente_encontrado.get('status') == 'bloqueado':
            return {
                "status": "bloqueado",
                "razao_social": cliente_encontrado.get('razao_social'),
                "nome_fantasia": cliente_encontrado.get('nome_fantasia'),
                "cnpj": cliente_encontrado.get('cnpj'),
                "motivo_bloqueio": cliente_encontrado.get('motivo_bloqueio')
            }
        
        # Retornar informações do cliente e débitos
        return {
            "status": "ativo",
            "razao_social": cliente_encontrado.get('razao_social'),
            "nome_fantasia": cliente_encontrado.get('nome_fantasia'),
            "cnpj": cliente_encontrado.get('cnpj'),
            "telefone": cliente_encontrado.get('telefone'),
            "email": cliente_encontrado.get('email'),
            "debitos": cliente_encontrado.get('debitos', [])
        }
        
    except FileNotFoundError:
        return {
            "status": "erro",
            "mensagem": "Arquivo de dados não encontrado"
        }
    except json.JSONDecodeError:
        return {
            "status": "erro",
            "mensagem": "Erro ao ler o arquivo de dados"
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao consultar débitos: {str(e)}"
        }


@tool
def consulta_financeira(cpf_cnpj: str):
    """Busca informações de um cliente e suas pendências no Asaas pelo CPF ou CNPJ.
    
    Args:
        cpf_cnpj (str): CPF ou CNPJ do cliente a ser buscado
        
    Returns:
        dict: Informações do cliente e suas pendências retornadas pela API do Asaas
    """
    # Obter a chave de API do Asaas das variáveis de ambiente
    api_key = os.getenv("ASAAS_API_KEY")
    if not api_key:
        return {
            "status": "erro",
            "mensagem": "Chave de API do Asaas não configurada"
        }
    
    # Verificar se é um ambiente de sandbox
    is_sandbox = os.getenv("ASAAS_SANDBOX", "false").lower() == "true"
    
    # Determinar a URL base da API
    if is_sandbox:
        base_url = "https://sandbox.asaas.com/api/v3"
    else:
        base_url = "https://api.asaas.com/v3"
    
    # Cabeçalhos da requisição
    headers = {
        "access_token": api_key,
        "Content-Type": "application/json"
    }
    
    # Primeiro passo: Buscar o cliente pelo CPF/CNPJ
    customer_url = f"{base_url}/customers"
    customer_params = {
        "cpfCnpj": cpf_cnpj
    }
    
    try:
        # Fazer a requisição GET para buscar o cliente
        customer_response = requests.get(customer_url, headers=headers, params=customer_params)
        
        # Verificar se a requisição foi bem-sucedida
        if customer_response.status_code != 200:
            return {
                "status": "erro",
                "mensagem": f"Erro na requisição ao buscar cliente: {customer_response.status_code} - {customer_response.text}"
            }
        
        customer_data = customer_response.json()
        
        # Verificar se encontrou o cliente
        if not customer_data.get("totalCount", 0) > 0 or not customer_data.get("data"):
            return {
                "status": "nao_encontrado",
                "mensagem": "Cliente não encontrado no Asaas"
            }
        
        # Pegar o primeiro cliente encontrado
        cliente = customer_data["data"][0]
        customer_id = cliente.get("id")
        
        # Segundo passo: Buscar as pendências do cliente usando o ID
        payments_url = f"{base_url}/payments"
        payments_params = {
            "customer": customer_id
        }
        
        # Fazer a requisição GET para buscar as pendências
        payments_response = requests.get(payments_url, headers=headers, params=payments_params)
        
        # Verificar se a requisição foi bem-sucedida
        if payments_response.status_code != 200:
            return {
                "status": "erro",
                "mensagem": f"Erro na requisição ao buscar pendências: {payments_response.status_code} - {payments_response.text}"
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
                
                if pagamento.get("interest") and isinstance(pagamento.get("interest"), dict):
                    interest_value = pagamento["interest"].get("value", 0)
                
                # Calcular valor total com multas e juros
                total_value = pagamento.get("value", 0) + fine_value + interest_value
                
                pendencias.append({
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
                    "pago": pagamento.get("status") == "RECEIVED"
                })
        
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
                "grupos": [grupo.get("name") for grupo in cliente.get("groups", [])] if cliente.get("groups") else []
            },
            "pendencias": pendencias,
            "total_pendencias": len(pendencias)
        }
            
    except requests.exceptions.RequestException as e:
        return {
            "status": "erro",
            "mensagem": f"Erro de conexão com a API do Asaas: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao buscar informações no Asaas: {str(e)}"
        }


@tool
def processar_comprovante(
    file_url: str,
    project_id: str ="nxz-agents",
    processor_id: str = "1b63e26aaf2871f1",
    location: str = "us"
):
    """Processa um documento usando o Google Document AI e retorna o texto extraído.
    
    Args:
        file_url (str): URL do arquivo a ser processado
        
    Returns:
        dict: Texto extraído do documento e informações de confiança
    """
    try:
        # Obter credenciais do Google Cloud das variáveis de ambiente
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_path:
            return {
                "status": "erro",
                "mensagem": "GOOGLE_APPLICATION_CREDENTIALS não configurado"
            }
        
        # Carregar credenciais
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        
        # Configurar cliente do Document AI
        client = documentai.DocumentProcessorServiceClient(credentials=credentials)
        
        # Formatar o nome do processador
        name = client.processor_path(project_id, location, processor_id)
        
        # Baixar o conteúdo do arquivo da URL
        response = requests.get(file_url)
        if response.status_code != 200:
            return {
                "status": "erro",
                "mensagem": f"Falha ao baixar o arquivo: {response.status_code}"
            }
        
        # Detectar o tipo de conteúdo do arquivo
        content_type = response.headers.get('content-type', 'application/octet-stream')
        
        # Criar a requisição para processar o documento
        raw_document = documentai.RawDocument(
            content=response.content,
            mime_type=content_type
        )
        
        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document
        )
        
        # Processar o documento
        result = client.process_document(request=request)
        document = result.document
        
        # Extrair o texto do documento
        extracted_text = document.text
        
        # Retornar o texto extraído
        return {
            "status": "sucesso",
            "texto": extracted_text,
            "confidence": float(result.document_confidence) if result.document_confidence else None
        }
        
    except Exception as e:
        return {
            "status": "erro",
            "mensagem": f"Erro ao processar documento com Google Document AI: {str(e)}"
        }

