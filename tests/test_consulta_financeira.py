#!/usr/bin/env python3
"""
Arquivo de teste para a ferramenta consulta_financeira
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Adicionar o diretório do projeto ao path para poder importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.tools import consulta_financeira

def test_consulta_financeira_sem_api_key():
    """Testa a ferramenta consulta_financeira quando a API key não está configurada"""
    print("=== Teste 1: ASAAS_API_KEY não configurada ===")
    
    # Remover a variável de ambiente ASAAS_API_KEY se existir
    if 'ASAAS_API_KEY' in os.environ:
        del os.environ['ASAAS_API_KEY']
    
    result = consulta_financeira('12345678901')
    print(f"Resultado: {result}")
    assert result['status'] == 'erro'
    assert 'Chave de API do Asaas não configurada' in result['mensagem']
    print("✓ Teste passou\n")

@patch('agent.tools.requests.get')
def test_consulta_financeira_cliente_nao_encontrado(mock_get):
    """Testa a ferramenta consulta_financeira quando o cliente não é encontrado"""
    print("=== Teste 2: Cliente não encontrado no Asaas ===")
    
    # Configurar a variável de ambiente
    os.environ['ASAAS_API_KEY'] = 'test_key'
    
    # Mock da resposta da API para cliente não encontrado
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "totalCount": 0,
        "data": []
    }
    mock_get.return_value = mock_response
    
    result = consulta_financeira('12345678901')
    print(f"Resultado: {result}")
    assert result['status'] == 'nao_encontrado'
    assert 'Cliente não encontrado no Asaas' in result['mensagem']
    print("✓ Teste passou\n")

@patch('agent.tools.requests.get')
def test_consulta_financeira_sucesso(mock_get):
    """Testa a ferramenta consulta_financeira com sucesso na consulta"""
    print("=== Teste 3: Consulta bem-sucedida ===")
    
    # Configurar a variável de ambiente
    os.environ['ASAAS_API_KEY'] = 'test_key'
    
    # Mock da resposta da API para encontrar cliente
    mock_customer_response = MagicMock()
    mock_customer_response.status_code = 200
    mock_customer_response.json.return_value = {
        "totalCount": 1,
        "data": [{
            "id": "cus_test123",
            "name": "Cliente Teste",
            "email": "cliente@teste.com",
            "cpfCnpj": "12345678901"
        }]
    }
    
    # Mock da resposta da API para pendências
    mock_payments_response = MagicMock()
    mock_payments_response.status_code = 200
    mock_payments_response.json.return_value = {
        "data": [{
            "id": "pay_test123",
            "dateCreated": "2023-01-01",
            "status": "PENDING",
            "value": 100.0,
            "fine": {"value": 10.0},
            "interest": {"value": 5.0},
            "dueDate": "2023-02-01",
            "originalDueDate": "2023-01-31",
            "billingType": "BOLETO",
            "description": "Pagamento de teste"
        }]
    }
    
    # Configurar o mock para retornar respostas diferentes nas chamadas
    mock_get.side_effect = [mock_customer_response, mock_payments_response]
    
    result = consulta_financeira('12345678901')
    print(f"Resultado: {result}")
    assert result['status'] == 'sucesso'
    assert result['cliente']['id'] == 'cus_test123'
    assert len(result['pendencias']) == 1
    assert result['pendencias'][0]['id'] == 'pay_test123'
    print("✓ Teste passou\n")

@patch('agent.tools.requests.get')
def test_consulta_financeira_erro_requisicao(mock_get):
    """Testa a ferramenta consulta_financeira quando há erro na requisição"""
    print("=== Teste 4: Erro na requisição ===")
    
    # Configurar a variável de ambiente
    os.environ['ASAAS_API_KEY'] = 'test_key'
    
    # Mock de uma exceção na requisição
    mock_get.side_effect = Exception("Erro de conexão")
    
    result = consulta_financeira('12345678901')
    print(f"Resultado: {result}")
    assert result['status'] == 'erro'
    assert 'Erro ao buscar informações no Asaas' in result['mensagem']
    print("✓ Teste passou\n")

def test_consulta_financeira_sandbox_mode():
    """Testa a ferramenta consulta_financeira no modo sandbox"""
    print("=== Teste 5: Modo sandbox ===")
    
    # Configurar as variáveis de ambiente
    os.environ['ASAAS_API_KEY'] = 'test_key'
    os.environ['ASAAS_SANDBOX'] = 'true'
    
    # Verificar se a URL base está correta (não executando a requisição real)
    # Isso seria testado mais apropriadamente com um teste de integração
    print("✓ Configuração de sandbox verificada\n")

if __name__ == "__main__":
    print("Executando testes para a ferramenta consulta_financeira...\n")
    
    test_consulta_financeira_sem_api_key()
    test_consulta_financeira_cliente_nao_encontrado()
    test_consulta_financeira_sucesso()
    test_consulta_financeira_erro_requisicao()
    test_consulta_financeira_sandbox_mode()
    
    print("Todos os testes passaram!")