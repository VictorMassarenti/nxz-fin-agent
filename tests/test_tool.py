#!/usr/bin/env python3
"""
Arquivo de teste para a ferramenta consultar_debitos_cliente
"""

import sys
import os

# Adicionar o diretório do projeto ao path para poder importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.tools import consultar_debitos_cliente

def test_tool():
    """Testa a ferramenta consultar_debitos_cliente com diferentes CNPJs"""
    
    # Teste com CNPJ válido do mock-data.json
    print("=== Teste 1: CNPJ válido (11.222.333/0001-81) ===")
    result = consultar_debitos_cliente('11.222.333/0001-81')
    print(f"Resultado: {result}")
    print()
    
    # Teste com CNPJ válido do mock-data.json (formato limpo)
    print("=== Teste 2: CNPJ válido (11222333000181) ===")
    result = consultar_debitos_cliente('11222333000181')
    print(f"Resultado: {result}")
    print()
    
    # Teste com CNPJ de cliente sem débitos
    print("=== Teste 3: CNPJ válido sem débitos (44.555.666/0001-92) ===")
    result = consultar_debitos_cliente('44.555.666/0001-92')
    print(f"Resultado: {result}")
    print()
    
    # Teste com CNPJ de cliente bloqueado
    print("=== Teste 4: CNPJ de cliente bloqueado (77.888.999/0001-03) ===")
    result = consultar_debitos_cliente('77.888.999/0001-03')
    print(f"Resultado: {result}")
    print()
    
    # Teste com CNPJ inválido
    print("=== Teste 5: CNPJ inválido (99.999.999/9999-99) ===")
    result = consultar_debitos_cliente('99.999.999/9999-99')
    print(f"Resultado: {result}")
    print()

if __name__ == "__main__":
    test_tool()