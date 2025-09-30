import os
import requests


def _db_url() -> str:
    user = os.getenv("DB_USER")
    pwd = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")

    base = f"postgresql://{user}:{pwd}@{host}:{port}/{name}"

    return base


def _conn():
    import psycopg
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
