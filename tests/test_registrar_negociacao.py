#!/usr/bin/env python3
"""
Arquivo de teste para a ferramenta registrar_negociacao
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Adicionar o diretório do projeto ao path para poder importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.tools import registrar_negociacao

@patch('agent.tools._conn')
def test_registrar_negociacao_sucesso(mock_conn):
    """Testa a ferramenta registrar_negociacao com sucesso"""
    print("=== Teste 1: Registro bem-sucedido ===")

    # Mock da conexão e cursor
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.return_value.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    cnpj = "12345678901234"
    detalhes = "Cliente acordou pagamento de 50% do valor em atraso até 15/01/2024"

    result = registrar_negociacao.invoke({"cnpj": cnpj, "detalhes": detalhes})

    print(f"Resultado: {result}")

    # Verificar se o cursor executou o SQL correto
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO negociacoes (cnpj, detalhes) VALUES (%s, %s)",
        (cnpj, detalhes)
    )

    # Verificar se o commit foi chamado
    mock_connection.commit.assert_called_once()

    # Verificar o retorno
    assert result['status'] == 'sucesso'
    assert result['message'] == 'Negociação registrada com sucesso'
    print("✓ Teste passou\n")

@patch('agent.tools._conn')
def test_registrar_negociacao_erro_conexao(mock_conn):
    """Testa a ferramenta registrar_negociacao quando há erro de conexão"""
    print("=== Teste 2: Erro de conexão ===")

    # Mock de uma exceção na conexão
    mock_conn.side_effect = Exception("Erro de conexão com o banco")

    cnpj = "12345678901234"
    detalhes = "Teste de negociação"

    try:
        result = registrar_negociacao.invoke({"cnpj": cnpj, "detalhes": detalhes})
        # Se não houve exceção, algo está errado
        assert False, "Deveria ter lançado exceção"
    except Exception as e:
        print(f"Exceção capturada: {e}")
        assert "Erro de conexão com o banco" in str(e)
        print("✓ Teste passou\n")

@patch('agent.tools._conn')
def test_registrar_negociacao_erro_sql(mock_conn):
    """Testa a ferramenta registrar_negociacao quando há erro SQL"""
    print("=== Teste 3: Erro SQL ===")

    # Mock da conexão e cursor
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.return_value.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    # Mock de erro SQL
    mock_cursor.execute.side_effect = Exception("Erro SQL: tabela não existe")

    cnpj = "12345678901234"
    detalhes = "Teste de negociação"

    try:
        result = registrar_negociacao.invoke({"cnpj": cnpj, "detalhes": detalhes})
        # Se não houve exceção, algo está errado
        assert False, "Deveria ter lançado exceção"
    except Exception as e:
        print(f"Exceção capturada: {e}")
        assert "Erro SQL" in str(e)
        print("✓ Teste passou\n")

@patch('agent.tools._conn')
def test_registrar_negociacao_cnpj_vazio(mock_conn):
    """Testa a ferramenta registrar_negociacao com CNPJ vazio"""
    print("=== Teste 4: CNPJ vazio ===")

    cnpj = ""
    detalhes = "Teste de negociação"

    result = registrar_negociacao.invoke({"cnpj": cnpj, "detalhes": detalhes})

    print(f"Resultado: {result}")

    # Não deve executar SQL nem fazer conexão com CNPJ vazio
    mock_conn.assert_not_called()

    # Verificar o retorno de erro
    assert result['status'] == 'erro'
    assert result['mensagem'] == 'CNPJ é obrigatório para registrar a negociação'
    print("✓ Teste passou\n")

@patch('agent.tools._conn')
def test_registrar_negociacao_cnpj_spaces(mock_conn):
    """Testa a ferramenta registrar_negociacao com CNPJ só com espaços"""
    print("=== Teste 5: CNPJ só com espaços ===")

    cnpj = "   "
    detalhes = "Teste de negociação"

    result = registrar_negociacao.invoke({"cnpj": cnpj, "detalhes": detalhes})

    print(f"Resultado: {result}")

    # Não deve executar SQL nem fazer conexão com CNPJ vazio
    mock_conn.assert_not_called()

    # Verificar o retorno de erro
    assert result['status'] == 'erro'
    assert result['mensagem'] == 'CNPJ é obrigatório para registrar a negociação'
    print("✓ Teste passou\n")

@patch('agent.tools._conn')
def test_registrar_negociacao_detalhes_longos(mock_conn):
    """Testa a ferramenta registrar_negociacao com detalhes longos"""
    print("=== Teste 6: Detalhes longos ===")

    # Mock da conexão e cursor
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.return_value.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    cnpj = "12345678901234"
    detalhes = "Cliente em situação financeira delicada. " * 100  # Texto longo

    result = registrar_negociacao.invoke({"cnpj": cnpj, "detalhes": detalhes})

    print(f"Resultado: {result}")

    # Verificar se o cursor executou o SQL
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO negociacoes (cnpj, detalhes) VALUES (%s, %s)",
        (cnpj, detalhes)
    )

    # Verificar se o commit foi chamado
    mock_connection.commit.assert_called_once()

    # Verificar o retorno
    assert result['status'] == 'sucesso'
    assert result['message'] == 'Negociação registrada com sucesso'
    print("✓ Teste passou\n")

if __name__ == "__main__":
    print("Executando testes para a ferramenta registrar_negociacao...\n")

    test_registrar_negociacao_sucesso()
    test_registrar_negociacao_erro_conexao()
    test_registrar_negociacao_erro_sql()
    test_registrar_negociacao_cnpj_vazio()
    test_registrar_negociacao_cnpj_spaces()
    test_registrar_negociacao_detalhes_longos()

    print("Todos os testes passaram!")